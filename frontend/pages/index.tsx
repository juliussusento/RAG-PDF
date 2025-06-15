import React from 'react';
import Head from 'next/head';
import FileUpload from '@/components/FileUpload';
import DocumentList from '@/components/DocumentList';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <Head>
        <title>RAG-based Financial Q&A System</title>
        <meta name="description" content="AI-powered Q&A system for financial documents" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          📊 Financial Q&A System (RAG)
        </h1>
        <p className="text-gray-600 mb-6">
          Upload PDF laporan keuangan dan mulai bertanya!
        </p>

        <section className="mb-8">
          <FileUpload
            onUploadComplete={() => window.location.reload()}
            onUploadError={(msg) => alert("Upload gagal: " + msg)}
          />
        </section>

        <section className="mb-8">
          <DocumentList />
        </section>

        <section>
          <ChatInterface />
        </section>
      </main>
    </div>
  );
}
