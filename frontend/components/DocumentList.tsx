import React, { useEffect, useState } from 'react';

interface DocumentInfo {
  filename: string;
  upload_date: string;
  chunks_count: number;
  status: string;
}

const DocumentList: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || ''}/api/documents`);
        const data = await res.json();
        setDocuments(data.documents);
      } catch (error) {
        console.error('Failed to fetch documents:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Uploaded Documents</h2>
      {isLoading ? (
        <p>Loading...</p>
      ) : documents.length === 0 ? (
        <p className="text-gray-500">No documents uploaded yet.</p>
      ) : (
        <ul className="space-y-4">
          {documents.map((doc) => (
            <li key={doc.filename} className="border p-4 rounded-md hover:shadow">
              <div className="font-medium">{doc.filename}</div>
              <div className="text-sm text-gray-600">Uploaded: {new Date(doc.upload_date).toLocaleString()}</div>
              <div className="text-sm text-gray-600">Status: {doc.status}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentList;
