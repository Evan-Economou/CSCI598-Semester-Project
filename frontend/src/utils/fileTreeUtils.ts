/**
 * Utility functions for building and managing file tree structures
 */
import { UploadedFile, FileTreeNode } from '../types';

/**
 * Build a hierarchical tree structure from a flat list of files
 * Only includes C++ files and their parent directories
 */
export function buildFileTree(files: UploadedFile[]): FileTreeNode[] {
  const root: Map<string, FileTreeNode> = new Map();
  const CPP_EXTENSIONS = ['.cpp', '.hpp', '.h'];

  // Filter to only C++ files
  const cppFiles = files.filter(file => {
    const fileName = file.file_path || file.file_name;
    return CPP_EXTENSIONS.some(ext => fileName.toLowerCase().endsWith(ext));
  });

  cppFiles.forEach(file => {
    const filePath = file.file_path || file.file_name;
    const parts = filePath.split(/[/\\]/); // Split on both / and \

    // Build path from root to file
    let currentPath = '';
    let currentLevel = root;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLastPart = i === parts.length - 1;
      currentPath = currentPath ? `${currentPath}/${part}` : part;

      if (isLastPart) {
        // This is the file itself
        const fileNode: FileTreeNode = {
          name: part,
          path: currentPath,
          type: 'file',
          file_id: file.file_id,
          file_size: file.file_size,
        };
        currentLevel.set(part, fileNode);
      } else {
        // This is a directory
        if (!currentLevel.has(part)) {
          const folderNode: FileTreeNode = {
            name: part,
            path: currentPath,
            type: 'folder',
            children: [],
          };
          currentLevel.set(part, folderNode);
        }

        const folderNode = currentLevel.get(part)!;
        if (!folderNode.children) {
          folderNode.children = [];
        }

        // Create a map for the next level
        const childrenMap = new Map<string, FileTreeNode>();
        folderNode.children.forEach(child => {
          childrenMap.set(child.name, child);
        });

        currentLevel = childrenMap;
      }
    }
  });

  // Convert map to sorted array
  const sortNodes = (nodes: Map<string, FileTreeNode>): FileTreeNode[] => {
    const sorted = Array.from(nodes.values()).sort((a, b) => {
      // Folders first, then files
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1;
      }
      // Alphabetical within same type
      return a.name.localeCompare(b.name);
    });

    // Recursively sort children
    sorted.forEach(node => {
      if (node.type === 'folder' && node.children) {
        const childrenMap = new Map<string, FileTreeNode>();
        node.children.forEach(child => {
          childrenMap.set(child.name, child);
        });
        node.children = sortNodes(childrenMap);
      }
    });

    return sorted;
  };

  return sortNodes(root);
}

/**
 * Find a file in the tree by file_id
 */
export function findFileInTree(tree: FileTreeNode[], fileId: string): FileTreeNode | null {
  for (const node of tree) {
    if (node.type === 'file' && node.file_id === fileId) {
      return node;
    }
    if (node.type === 'folder' && node.children) {
      const found = findFileInTree(node.children, fileId);
      if (found) return found;
    }
  }
  return null;
}

/**
 * Remove a file from the tree by file_id
 * Returns a new tree with the file removed and empty folders cleaned up
 */
export function removeFileFromTree(tree: FileTreeNode[], fileId: string): FileTreeNode[] {
  const filtered = tree
    .map(node => {
      if (node.type === 'file') {
        // Keep file if it's not the one being deleted
        return node.file_id === fileId ? null : node;
      } else {
        // Recursively filter children
        const newChildren = node.children
          ? removeFileFromTree(node.children, fileId)
          : [];

        // Only keep folder if it has children
        if (newChildren.length > 0) {
          return {
            ...node,
            children: newChildren,
          };
        }
        return null;
      }
    })
    .filter((node): node is FileTreeNode => node !== null);

  return filtered;
}
