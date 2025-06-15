import React, { useState } from 'react';

interface FileUploadProps {
  onUploadComplete?: (data: any) => void;
  onUploadError?: (message: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadComplete,
  onUploadError,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (selected.type !== 'application/pdf') {
      onUploadError?.('Only PDF files are allowed.');
      return;
    }

    if (selected.size > 10 * 1024 * 1024) {
      onUploadError?.('File size exceeds 10MB.');
      return;
    }

    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const result = await response.json();
      onUploadComplete?.(result);
    } catch (err: any) {
      onUploadError?.(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(100);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto bg-white shadow-md rounded-lg p-6">
      <div
        className="border-2 border-dashed border-gray-300 p-6 text-center rounded-md cursor-pointer hover:border-blue-500 transition"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => document.querySelector('input[type="file"]')?.click()}
      >
        <p className="text-gray-700">📄 Drag & drop PDF here or click to select</p>
        {file?.name && <p className="mt-2 text-blue-600 font-medium">{file.name}</p>}
      </div>

      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      <div className="mt-4 flex justify-center">
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="px-6 py-2 bg-green-600 text-white font-semibold rounded hover:bg-green-700 disabled:opacity-50"
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      {isUploading && (
        <div className="mt-4">
          <progress value={uploadProgress} max={100} className="w-full h-2" />
        </div>
      )}
    </div>
  );
};

export default FileUpload;
