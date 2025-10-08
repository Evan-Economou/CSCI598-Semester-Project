/**
 * Utility functions for building and managing file tree structures
 */
import { UploadedFile, FileTreeNode } from '../types';

/**
 * Build a hierarchical tree structure from a flat list of files
 * Only includes C++ files and their parent directories
 */
export function buildFileTree(files: UploadedFile[]): FileTreeNode[] {
  const CPP_EXTENSIONS = ['.cpp', '.hpp', '.h'];

  // Filter to only C++ files
  const cppFiles = files.filter(file => {
    const fileName = file.file_path || file.file_name;
    return CPP_EXTENSIONS.some(ext => fileName.toLowerCase().endsWith(ext));
  });

  // Use a string-keyed map to store all nodes by their full path
  const nodeMap = new Map<string, FileTreeNode>();
  const rootNodes: FileTreeNode[] = [];

  cppFiles.forEach(file => {
    const filePath = file.file_path || file.file_name;
    const parts = filePath.split(/[/\\]/).filter(p => p.length > 0); // Split and remove empty parts

    // Build path from root to file
    let currentPath = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLastPart = i === parts.length - 1;
      const parentPath = currentPath;
      currentPath = currentPath ? `${currentPath}/${part}` : part;

      // Skip if node already exists
      if (nodeMap.has(currentPath)) {
        continue;
      }

      if (isLastPart) {
        // This is the file itself
        const fileNode: FileTreeNode = {
          name: part,
          path: currentPath,
          type: 'file',
          file_id: file.file_id,
          file_size: file.file_size,
        };
        nodeMap.set(currentPath, fileNode);

        // Add to parent's children or root
        if (parentPath) {
          const parent = nodeMap.get(parentPath);
          if (parent && parent.children) {
            parent.children.push(fileNode);
          }
        } else {
          rootNodes.push(fileNode);
        }
      } else {
        // This is a directory
        const folderNode: FileTreeNode = {
          name: part,
          path: currentPath,
          type: 'folder',
          children: [],
        };
        nodeMap.set(currentPath, folderNode);

        // Add to parent's children or root
        if (parentPath) {
          const parent = nodeMap.get(parentPath);
          if (parent && parent.children) {
            parent.children.push(folderNode);
          }
        } else {
          rootNodes.push(folderNode);
        }
      }
    }
  });

  // Sort function
  const sortNodes = (nodes: FileTreeNode[]): FileTreeNode[] => {
    const sorted = nodes.sort((a, b) => {
      // Folders first, then files
      if (a.type !== b.type) {
        return a.type === 'folder' ? -1 : 1;
      }
      // Alphabetical within same type
      return a.name.localeCompare(b.name);
    });

    // Recursively sort children
    sorted.forEach(node => {
      if (node.type === 'folder' && node.children && node.children.length > 0) {
        node.children = sortNodes(node.children);
      }
    });

    return sorted;
  };

  return sortNodes(rootNodes);
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
