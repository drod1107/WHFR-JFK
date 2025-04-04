#!/bin/bash
# backup_chroma.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="chroma_backups"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create a tarball of the ChromaDB data
tar -czf "$BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz" -C shared chroma_data

# Output backup location
echo "✅ ChromaDB backup created at $BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz"
echo "📋 To restore this backup, extract it back to the shared directory:"
echo "   tar -xzf $BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz -C shared"