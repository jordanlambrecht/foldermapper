from foldermapper import setup_environment, load_config, save_config, create_ignore_file, create_output_directory, generate_tree_map

if __name__ == '__main__':
    setup_environment()
    config = load_config()

    # Prompt for user input and update config as needed

    create_ignore_file()
    create_output_directory()

    stats = generate_tree_map(root_directory, **config)

    # Output stats and save updated config
    save_config(config)
