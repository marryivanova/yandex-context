def dino_run(
    count_barrier: int,
    start_barrier: list[int],
    type_barrier: list[int],
    count_jump: int,
    start_jump: list[int],
    distance_jump: list[int],
) -> int:
    len_step = {1: 1, 2: 2, 3: 4}
    points = {1: 1, 2: 3, 3: 5}
    barrier_end = [start_barrier[i] + len_step[type_barrier[i]] - 1 for i in range(count_barrier)]
    for i in range(count_barrier - 1):
        if start_barrier[i + 1] <= barrier_end[i]:
            return 0
    total_score = 0
    barrier_idx = 0
    current_pos = 1
    for jump in range(count_jump):
        jump_start = start_jump[jump]
        jump_dist = distance_jump[jump]
        jump_end = jump_start + jump_dist - 1
        if jump_start < current_pos:
            continue
        while barrier_idx < count_barrier and barrier_end[barrier_idx] < jump_start:
            total_score -= 1
            barrier_idx += 1
        if barrier_idx < count_barrier and start_barrier[barrier_idx] < jump_start:
            total_score -= 1
            barrier_idx += 1
        while barrier_idx < count_barrier:
            if start_barrier[barrier_idx] > jump_end:
                break
            if jump_start <= start_barrier[barrier_idx] and jump_end >= barrier_end[barrier_idx]:
                total_score += points[type_barrier[barrier_idx]]
            else:
                total_score -= 1
            barrier_idx += 1
        current_pos = jump_end + 1
    while barrier_idx < count_barrier:
        total_score -= 1
        barrier_idx += 1
    return max(0, total_score)
