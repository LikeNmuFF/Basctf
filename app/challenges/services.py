from datetime import datetime, timedelta
from math import ceil
from sqlalchemy import func, or_
from ..models import Challenge, FlagSubmission, Solve, HintUsage
from ..extensions import db
from ..utils import verify_flag

FREE_ATTEMPTS_BEFORE_COOLDOWN = 3
COOLDOWN_SECONDS = 5


def _build_challenge_query(category: str | None = None, difficulty: str | None = None, search: str | None = None):
    query = Challenge.query.filter_by(is_active=True)

    if category and category != 'all':
        query = query.filter(Challenge.category == category)

    if difficulty and difficulty != 'all':
        query = query.filter(Challenge.difficulty == difficulty)

    if search:
        term = f'%{search.strip()}%'
        query = query.filter(or_(Challenge.title.ilike(term), Challenge.description.ilike(term)))

    return query.order_by(Challenge.points.asc(), Challenge.title.asc())


def get_all_active_challenges():
    """Return all active challenges ordered by points."""
    return _build_challenge_query().all()


def get_challenge_by_id(challenge_id: int):
    """Return a single challenge or 404."""
    return Challenge.query.get_or_404(challenge_id)


def user_has_solved(user_id: int, challenge_id: int) -> bool:
    """Check if a user already solved a given challenge."""
    return Solve.query.filter_by(user_id=user_id, challenge_id=challenge_id).first() is not None


def _get_recent_submissions(user_id: int, challenge_id: int):
    return FlagSubmission.query.filter_by(
        user_id=user_id,
        challenge_id=challenge_id
    ).order_by(FlagSubmission.submitted_at.desc()).all()


def get_failed_streak(user_id: int, challenge_id: int) -> int:
    streak = 0
    for submission in _get_recent_submissions(user_id, challenge_id):
        if submission.is_correct:
            break
        streak += 1
    return streak


def get_cooldown_remaining(user_id: int, challenge_id: int) -> int:
    latest_submission = FlagSubmission.query.filter_by(
        user_id=user_id,
        challenge_id=challenge_id
    ).order_by(FlagSubmission.submitted_at.desc()).first()

    if latest_submission is None or latest_submission.is_correct:
        return 0

    failed_streak = get_failed_streak(user_id, challenge_id)
    if failed_streak < FREE_ATTEMPTS_BEFORE_COOLDOWN:
        return 0

    cooldown_ends_at = latest_submission.submitted_at + timedelta(seconds=COOLDOWN_SECONDS)
    remaining = ceil((cooldown_ends_at - datetime.utcnow()).total_seconds())
    return max(0, remaining)


def get_hint_usage(user_id: int, challenge_id: int) -> HintUsage:
    usage = HintUsage.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()
    if not usage:
        usage = HintUsage(user_id=user_id, challenge_id=challenge_id, used_hints=0)
        db.session.add(usage)
        db.session.commit()
    return usage


HINT_COSTS = {
    1: 25,
    2: 50,
    3: 100,
}


def request_hint(user, challenge, hint_number: int) -> tuple[bool, str]:
    """Give a hint and deduct points from the user score."""
    if hint_number not in HINT_COSTS:
        return False, 'Hint number must be 1, 2, or 3.'

    if user_has_solved(user.id, challenge.id):
        return False, 'You already solved this challenge; no more hints are needed.'

    usage = get_hint_usage(user.id, challenge.id)
    if hint_number <= usage.used_hints:
        return False, 'This hint is already unlocked.'

    if hint_number != usage.used_hints + 1:
        return False, 'Hints must be taken in order: 1, then 2, then 3.'

    hint_text = None
    if hint_number == 1:
        hint_text = challenge.hint_1
    elif hint_number == 2:
        hint_text = challenge.hint_2
    elif hint_number == 3:
        hint_text = challenge.hint_3

    if not hint_text:
        return False, 'No hint text available for this level yet.'

    cost = HINT_COSTS[hint_number]
    if cost >= user.score:
        return False, 'Insufficient Points'
    user.score = user.score - cost
    usage.used_hints = hint_number
    db.session.commit()

    return True, f'Hint {hint_number} (−{cost} points): {hint_text}'


def submit_flag(user, challenge, submitted_flag: str) -> tuple[bool, str]:
    """
    Attempt flag submission.
    Returns (success: bool, message: str)
    """
    if user_has_solved(user.id, challenge.id):
        return False, 'You have already solved this challenge!'

    cooldown_remaining = get_cooldown_remaining(user.id, challenge.id)
    if cooldown_remaining > 0:
        return False, f'Too many wrong flags in a row. Wait {cooldown_remaining} seconds before trying again.'

    is_correct = verify_flag(submitted_flag, challenge.flag_hash)
    submission = FlagSubmission(
        user_id=user.id,
        challenge_id=challenge.id,
        is_correct=is_correct
    )
    db.session.add(submission)

    if is_correct:
        solve = Solve(user_id=user.id, challenge_id=challenge.id)
        user.score += challenge.points
        db.session.add(solve)
        db.session.commit()
        return True, f'Correct! You earned {challenge.points} points!'

    db.session.commit()

    failed_streak = get_failed_streak(user.id, challenge.id)
    if failed_streak >= FREE_ATTEMPTS_BEFORE_COOLDOWN:
        return False, f'Incorrect flag. Cooldown applied: wait {COOLDOWN_SECONDS} seconds before the next try.'
    return False, 'Incorrect flag. Keep trying!'


def get_solved_ids_for_user(user_id: int) -> set:
    """Return set of challenge IDs solved by a user."""
    solves = Solve.query.filter_by(user_id=user_id).all()
    return {s.challenge_id for s in solves}


def get_challenges_filtered(category: str | None = None, difficulty: str | None = None, search: str | None = None):
    """Return filtered active challenges (no grouping)."""
    return _build_challenge_query(category, difficulty, search).all()


def get_challenges_by_category(category: str | None = None, difficulty: str | None = None, search: str | None = None):
    """Return challenges grouped by category."""
    challenges = get_challenges_filtered(category, difficulty, search)
    grouped = {}
    for ch in challenges:
        grouped.setdefault(ch.category, []).append(ch)
    return grouped


def get_submission_stats_for_user(user_id: int) -> dict:
    submissions = FlagSubmission.query.filter_by(user_id=user_id).order_by(
        FlagSubmission.submitted_at.asc(),
        FlagSubmission.id.asc()
    ).all()
    total_submissions = FlagSubmission.query.filter_by(user_id=user_id).count()
    correct_submissions = FlagSubmission.query.filter_by(user_id=user_id, is_correct=True).count()
    wrong_submissions = total_submissions - correct_submissions
    accuracy = round((correct_submissions / total_submissions) * 100, 2) if total_submissions else 0.0
    chart_points = []
    correct_so_far = 0

    for index, submission in enumerate(submissions, start=1):
        if submission.is_correct:
            correct_so_far += 1
        chart_points.append({
            'attempt': index,
            'accuracy': round((correct_so_far / index) * 100, 2)
        })

    most_targeted = db.session.query(
        Challenge.title,
        func.count(FlagSubmission.id).label('attempts')
    ).join(
        Challenge, Challenge.id == FlagSubmission.challenge_id
    ).filter(
        FlagSubmission.user_id == user_id
    ).group_by(
        Challenge.id, Challenge.title
    ).order_by(
        func.count(FlagSubmission.id).desc(),
        Challenge.title.asc()
    ).first()

    return {
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'wrong_submissions': wrong_submissions,
        'accuracy': accuracy,
        'most_targeted': most_targeted,
        'chart_points': chart_points,
    }


def get_challenge_rating_stats(challenge_id: int) -> dict:
    """
    Get rating statistics for a challenge.
    Returns dict with like_count, dislike_count, total_votes, like_percentage
    """
    from ..models import ChallengeRating
    
    likes = ChallengeRating.query.filter_by(challenge_id=challenge_id, rating=True).count()
    dislikes = ChallengeRating.query.filter_by(challenge_id=challenge_id, rating=False).count()
    total_votes = likes + dislikes
    
    like_percentage = 0
    if total_votes > 0:
        like_percentage = round((likes / total_votes) * 100)
    
    return {
        'like_count': likes,
        'dislike_count': dislikes,
        'total_votes': total_votes,
        'like_percentage': like_percentage
    }


def get_user_challenge_rating(user_id: int, challenge_id: int) -> bool | None:
    """
    Get current user's rating for a challenge.
    Returns True for like, False for dislike, None if not rated
    """
    from ..models import ChallengeRating
    
    rating = ChallengeRating.query.filter_by(
        user_id=user_id, 
        challenge_id=challenge_id
    ).first()
    
    return rating.rating if rating else None


def rate_challenge(user_id: int, challenge_id: int, rating_value: bool) -> tuple[bool, str]:
    """
    Rate a challenge (like or dislike).
    If user already rated, update their rating.
    Returns (success: bool, message: str)
    """
    from ..models import ChallengeRating, Challenge, User
    from ..extensions import db
    
    # Validate challenge exists and is active
    challenge = Challenge.query.get(challenge_id)
    if not challenge or not challenge.is_active:
        return False, 'Challenge not found or not available'
    
    # Validate user exists
    user = User.query.get(user_id)
    if not user:
        return False, 'User not found'
    
    # Check if user already rated this challenge
    existing_rating = ChallengeRating.query.filter_by(
        user_id=user_id,
        challenge_id=challenge_id
    ).first()
    
    if existing_rating:
        # Update existing rating
        if existing_rating.rating == rating_value:
            # User clicked the same button again - remove rating (toggle off)
            db.session.delete(existing_rating)
            db.session.commit()
            action = 'removed'
        else:
            # User changed their rating
            existing_rating.rating = rating_value
            db.session.commit()
            action = 'updated'
    else:
        # Create new rating
        new_rating = ChallengeRating(
            user_id=user_id,
            challenge_id=challenge_id,
            rating=rating_value
        )
        db.session.add(new_rating)
        db.session.commit()
        action = 'added'
    
    # Get updated stats
    stats = get_challenge_rating_stats(challenge_id)
    
    if action == 'removed':
        message = 'Your rating has been removed'
    elif action == 'updated':
        message = 'Your rating has been updated'
    else:
        message = 'Your rating has been recorded'
    
    return True, {
        'message': message,
        'action': action,
        'user_rating': rating_value if action != 'removed' else None,
        'stats': stats
    }


def remove_challenge_rating(user_id: int, challenge_id: int) -> tuple[bool, str]:
    """
    Remove user's rating for a challenge.
    Returns (success: bool, message: str)
    """
    from ..models import ChallengeRating
    from ..extensions import db
    
    rating = ChallengeRating.query.filter_by(
        user_id=user_id,
        challenge_id=challenge_id
    ).first()
    
    if not rating:
        return False, 'You have not rated this challenge'
    
    db.session.delete(rating)
    db.session.commit()
    
    stats = get_challenge_rating_stats(challenge_id)
    
    return True, {
        'message': 'Your rating has been removed',
        'stats': stats
    }
