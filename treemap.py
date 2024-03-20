def generate_tree_map(root_dir, prefix='', max_depth=None, show_files=True, show_hidden=False, file_limit=None, style='basic', vertical_connectors=False, depth=0, stats={'main folders': 0, 'sub folders': 0, 'files': 0, 'deepest': 0}):
    if max_depth is not None and depth >= max_depth:
        return
    files = sorted(os.listdir(root_dir))
    if not show_hidden:
        files = [f for f in files if not f.startswith('.')]
    files = [f for f in files if show_files or os.path.isdir(os.path.join(root_dir, f))]
    stats['sub folders'] += 1 if depth > 0 else 0
    stats['main folders'] += 1 if depth == 0 else 0
    stats['deepest'] = max(stats['deepest'], depth)
    displayed_files = 0
    color = DEPTH_COLORS[depth % len(DEPTH_COLORS)] if depth < len(DEPTH_COLORS) else DEPTH_COLORS[-1]
    for i, file in enumerate(files):
        is_last_item = i == len(files) - 1
        connector = '└──' if is_last_item else '├──'
        print(f"{prefix}{color}{connector}{Colors.ENDC} {file}")
        displayed_files += 1
        if file_limit is not None and displayed_files >= file_limit:
            break
        if os.path.isdir(os.path.join(root_dir, file)):
            extension = '    ' if is_last_item else '│   '
            generate_tree_map(os.path.join(root_dir, file), prefix + extension, max_depth, show_files, show_hidden, file_limit, style, vertical_connectors, depth + 1, stats)
        else:
            stats['files'] += 1
    return stats
