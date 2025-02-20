#!/bin/bash
set -e

# Use environment variables or fallback to default values
TARGET_UID=${UID:-1000}
TARGET_GID=${GID:-1000}

echo "Container starting with UID: $TARGET_UID and GID: $TARGET_GID"

# Update the group ID if necessary
CURRENT_GID=$(id -g myuser)
if [ "$CURRENT_GID" -ne "$TARGET_GID" ]; then
    echo "Changing group ID of 'myuser' from $CURRENT_GID to $TARGET_GID"
    groupmod -g $TARGET_GID mygroup
fi

# Update the user ID if necessary
CURRENT_UID=$(id -u myuser)
if [ "$CURRENT_UID" -ne "$TARGET_UID" ]; then
    echo "Changing user ID of 'myuser' from $CURRENT_UID to $TARGET_UID"
    usermod -u $TARGET_UID myuser
fi

# Update ownership for application files
chown -R myuser:mygroup /code/data

# Drop privileges and run the passed command as the updated user
exec gosu myuser "$@"
