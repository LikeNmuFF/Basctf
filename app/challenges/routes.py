from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import challenges_bp
from .services import (
    get_all_active_challenges, get_challenge_by_id,
    submit_flag, get_solved_ids_for_user, get_challenges_by_category,
    get_cooldown_remaining, request_hint, get_hint_usage
)
from ..utils import CATEGORIES, DIFFICULTIES


@challenges_bp.route('/')
@login_required
def list_challenges():
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('q', '').strip()

    valid_categories = {c[0] for c in CATEGORIES}
    valid_difficulties = {d[0] for d in DIFFICULTIES}
    if category not in valid_categories and category != 'all':
        category = 'all'
    if difficulty not in valid_difficulties and difficulty != 'all':
        difficulty = 'all'

    grouped = get_challenges_by_category(category, difficulty, search)
    visible_count = sum(len(lst) for lst in grouped.values())
    total_count = len(get_all_active_challenges())
    solved_ids = get_solved_ids_for_user(current_user.id)
    
    # Get recent solves for the sidebar (last 10 solves from active challenges)
    from ..models import Solve, User, Challenge
    recent_solves = Solve.query.join(User).join(Challenge).filter(
        Challenge.is_active == True
    ).order_by(
        Solve.solved_at.desc()
    ).limit(10).all()

    return render_template(
        'challenges.html',
        grouped=grouped,
        solved_ids=solved_ids,
        recent_solves=recent_solves,
        filters={
            'category': category,
            'difficulty': difficulty,
            'q': search,
        },
        categories=CATEGORIES,
        difficulties=DIFFICULTIES,
        visible_count=visible_count,
        total_count=total_count,
    )


@challenges_bp.route('/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def challenge_detail(challenge_id):
    challenge = get_challenge_by_id(challenge_id)
    solved = get_solved_ids_for_user(current_user.id)
    already_solved = challenge.id in solved

    if request.method == 'POST':
        if already_solved:
            flash('You already solved this challenge!', 'info')
            return redirect(url_for('challenges.challenge_detail', challenge_id=challenge.id))

        submitted_flag = request.form.get('flag', '').strip()
        if not submitted_flag:
            flash('Please enter a flag.', 'warning')
            return redirect(url_for('challenges.challenge_detail', challenge_id=challenge.id))

        success, message = submit_flag(current_user, challenge, submitted_flag)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('challenges.challenge_detail', challenge_id=challenge.id))

    cooldown_remaining = 0 if already_solved else get_cooldown_remaining(current_user.id, challenge.id)
    hint_usage = get_hint_usage(current_user.id, challenge.id)
    return render_template(
        'challenge_detail.html',
        challenge=challenge,
        already_solved=already_solved,
        cooldown_remaining=cooldown_remaining,
        hint_usage=hint_usage
    )


@challenges_bp.route('/<int:challenge_id>/hint/<int:hint_number>', methods=['POST'])
@login_required
def challenge_hint(challenge_id, hint_number):
    challenge = get_challenge_by_id(challenge_id)
    already_solved = challenge.id in get_solved_ids_for_user(current_user.id)

    success, message = request_hint(current_user, challenge, hint_number)
    flash(message, 'success' if success else 'danger')

    return redirect(url_for('challenges.challenge_detail', challenge_id=challenge.id))


@challenges_bp.route('/<int:challenge_id>/rate', methods=['POST'])
@login_required
def rate_challenge_route(challenge_id):
    from .services import rate_challenge, get_challenge_rating_stats, get_user_challenge_rating, remove_challenge_rating
    from ..models import Challenge
    from flask import jsonify
    
    challenge = Challenge.query.get(challenge_id)
    if not challenge or not challenge.is_active:
        return jsonify({'error': 'Challenge not available'}), 404
    
    data = request.get_json()
    if not data or 'rating' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    rating_value = data['rating']
    if rating_value not in ['like', 'dislike', 'remove']:
        return jsonify({'error': 'Invalid rating value'}), 400
    
    if rating_value == 'remove':
        success, result = remove_challenge_rating(current_user.id, challenge_id)
    else:
        # Convert string to boolean: True for like, False for dislike
        bool_rating = (rating_value == 'like')
        success, result = rate_challenge(current_user.id, challenge_id, bool_rating)
    
    if not success:
        return jsonify({'error': result.get('message', 'Unknown error')}), 400
    
    # Get updated stats and user's current rating
    stats = get_challenge_rating_stats(challenge_id)
    user_rating = get_user_challenge_rating(current_user.id, challenge_id)
    
    return jsonify({
        'success': True,
        'message': result.get('message'),
        'stats': stats,
        'user_rating': user_rating  # True for like, False for dislike, None for no rating
    })


@challenges_bp.route('/<int:challenge_id>/rating', methods=['GET'])
@login_required
def get_challenge_rating(challenge_id):
    from .services import get_challenge_rating_stats, get_user_challenge_rating
    from ..models import Challenge
    from flask import jsonify
    
    challenge = Challenge.query.get(challenge_id)
    if not challenge or not challenge.is_active:
        return jsonify({'error': 'Challenge not available'}), 404
    
    stats = get_challenge_rating_stats(challenge_id)
    user_rating = get_user_challenge_rating(current_user.id, challenge_id)
    
    return jsonify({
        'success': True,
        'stats': stats,
        'user_rating': user_rating  # True for like, False for dislike, None for no rating
    })
