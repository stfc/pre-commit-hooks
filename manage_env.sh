#!/bin/bash

if [ "$0" != "$BASH_SOURCE" ]; then
    echo "Error: Please run script with \`bash manage_env.sh\` rather than sourcing it"
    return
fi

# Exit script if any statement returns a non-true value:
set -e

# Use this script to create, update or delete a conda environment based on the
# following requirements file:
ENV_FILE='environment.yml'

source_conda() {
    # Finds and sources conda so we can subsequently use it to manage
    # a dedicated virtual environment for our package.

    # Enable conda
    {  # try
        source "$(conda info --base)/etc/profile.d/conda.sh"
    } || {  # catch
        echo "ERROR: No conda install found"
        exit 1
    }

    return 0
}

get_env_name() {
    # Retrieves the environment name from the requirements file.

    first_line=$(sed -n '1p' $ENV_FILE)
    ENV_NAME=${first_line#"name: "}
    echo "$ENV_NAME"
    return 0
}

install_this_package() {
    # Installs the package from this repository, either as a static version
    # or via symlink for dev mode.

    echo "Installing package in $1 environment..."
    conda activate "$1"

    case "$2" in
    dev)
        pip install -e .
        ;;

    stable)
        pip install .
        ;;

    *)
        echo "invalid mode provided for install_this_package() - need dev or stable"
        ;;

    esac

    return 0
}

create_env() {
    # Creates a conda environment from the requirements file hard-coded at the
    # top of this script.

    echo "Creating environment '$1'..."
    conda env create --force -f $ENV_FILE
    conda activate "$1"
    pip install -r requirements

    if [ "$2" = dev ]; then
        install_this_package "$ENV_NAME" dev
        echo "Installing pre-commit..."
        pre-commit install
    else
        install_this_package "$ENV_NAME" stable
    fi

    echo "#"
    echo "# Installation complete!"
    echo "#"
    echo "# To activate environment, use"
    echo "#     $ conda activate $ENV_NAME"
    echo "#"

    return 0
}

delete_env() {
    # Deletes the conda environment.
    # NOTE: This requires the conda environment to have the same name as the
    # python package contained within this repo.

    echo "Deleting environment '$1'"

    echo "Are you sure? YES/NO"
    read confirm
    if [ "$confirm" = YES ]; then
        conda deactivate
        conda env remove --name "$1"
    else
        echo "Aborting"
        exit 2
    fi

    return 0
}

check_args() {
    # Checks we've been given the right arguments for this script.

    if [ "$#" -ne 1 ]; then
        echo "Invalid number of arguments. Expects one argument ('install', 'develop' or 'uninstall')"
        exit 1
    fi
}

check_dir() {
    # Checks we're in the right directory for this script.

    [[ -e $ENV_FILE ]] || {
        echo >&2 "Please cd into the directory containing this script before running"
        exit 1
    }
}

main() {
    # Manages conda environment creation and deletion.

    check_args "$@" # check provided args

    check_dir # check we're in the right working directory

    source_conda # find and activate conda

    ENV_NAME=$(get_env_name)

    case "$1" in
    install)
        create_env "$ENV_NAME" stable
        ;;

    develop)
        create_env "$ENV_NAME" dev
        ;;

    uninstall)
        delete_env "$ENV_NAME"
        ;;

    *)
        echo "Invalid mode provided (need 'install', 'develop' or 'uninstall')"
        exit 1
        ;;

    esac

    exit 0
}

main "$@"
