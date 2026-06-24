import React, { useRef, useState } from 'react';
import { UploadCloud, X, FileText } from 'lucide-react';
import { formatBytes } from '../utils/format.utils';

interface FileDropZoneProps {
  onFileSelect: (file: File) => void;
  accept?: string[];
  maxSizeMB?: number;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({
  onFileSelect,
  accept = ['.pdf', '.docx'],
  maxSizeMB = 10,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = (file: File): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!accept.includes(ext)) return `Only ${accept.join(', ')} files are supported.`;
    if (file.size > maxSizeMB * 1024 * 1024) return `File is too large. Maximum size is ${maxSizeMB}MB.`;
    return null;
  };

  const handleFile = (file: File) => {
    const err = validate(file);
    if (err) { setError(err); setSelectedFile(null); return; }
    setError(null);
    setSelectedFile(file);
    onFileSelect(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const clear = () => {
    setSelectedFile(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="w-full">
      <div
        onClick={() => !selectedFile && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`relative min-h-[240px] rounded-lg border-2 border-dashed transition-all duration-200 flex flex-col items-center justify-center cursor-pointer
          ${dragging
            ? 'border-primary bg-primary/5 glow-primary'
            : selectedFile
              ? 'border-success/40 bg-success/5'
              : 'border-border-accent hover:border-primary/50 hover:bg-primary/5'
          }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept.join(',')}
          className="hidden"
          onChange={onInputChange}
          aria-label="Upload resume file"
        />

        {selectedFile ? (
          <div className="flex flex-col items-center gap-3 p-6 text-center">
            <FileText size={40} className="text-success" />
            <div>
              <p className="font-medium text-text-primary">{selectedFile.name}</p>
              <p className="text-sm text-text-muted mt-1">{formatBytes(selectedFile.size)}</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/20 text-success border border-success/30 uppercase">
              {selectedFile.name.split('.').pop()}
            </span>
            <button
              onClick={(e) => { e.stopPropagation(); clear(); }}
              className="mt-2 flex items-center gap-1.5 text-sm text-text-muted hover:text-danger transition-colors"
            >
              <X size={14} /> Remove
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 p-8 text-center">
            <UploadCloud size={48} className={dragging ? 'text-primary' : 'text-text-muted'} />
            <div>
              <p className="font-medium text-text-primary">Drop your resume here</p>
              <p className="text-sm text-text-muted mt-1">or click to browse</p>
            </div>
            <p className="text-xs text-text-muted">PDF or DOCX, max {maxSizeMB}MB</p>
          </div>
        )}
      </div>
      {error && (
        <p className="mt-2 text-sm text-danger flex items-center gap-1.5">
          <span>⚠</span> {error}
        </p>
      )}
    </div>
  );
};
