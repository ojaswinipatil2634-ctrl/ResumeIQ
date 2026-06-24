import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { uploadResume } from '../services/resume.service';
import { useResume } from '../hooks/useResume';
import { AppLayout } from '../layouts/Layouts';
import { FileDropZone } from '../components/FileDropZone';
import { Button } from '../components/ui/Button';

const errorMessages: Record<number, string> = {
  400: 'Only PDF and DOCX files are supported.',
  413: 'File is too large. Maximum size is 10MB.',
  422: 'No readable text found in this file. It may be a scanned image.',
};

export const UploadPage: React.FC = () => {
  const { setCurrentResume } = useResume();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const data = await uploadResume(file, setProgress);
      setCurrentResume(data.resume.id, data.resume.original_filename);
      // Cache skills count placeholder
      setSuccess(true);
      setTimeout(() => navigate(`/analysis/${data.resume.id}`), 1500);
    } catch (err: any) {
      const status = err.response?.status;
      setError(errorMessages[status] || err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Upload Resume</h1>
          <p className="text-text-muted text-sm mt-1">Upload your resume to get a full AI-powered analysis.</p>
        </div>

        {success ? (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-12 flex flex-col items-center gap-4 text-center">
            <div className="w-16 h-16 rounded-full bg-success/20 border border-success/30 flex items-center justify-center">
              <CheckCircle size={32} className="text-success" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary">Resume uploaded successfully!</h2>
            <p className="text-text-muted text-sm">Redirecting to your analysis...</p>
          </motion.div>
        ) : (
          <div className="flex flex-col gap-6">
            <FileDropZone onFileSelect={setFile} />

            {uploading && (
              <div className="flex flex-col gap-2">
                <div className="flex justify-between text-xs text-text-muted">
                  <span>Uploading...</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 bg-bg-elevated rounded-full overflow-hidden">
                  <motion.div className="h-full gradient-bg rounded-full"
                    initial={{ width: '0%' }} animate={{ width: `${progress}%` }}
                    transition={{ ease: 'linear' }} />
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-start gap-3 p-4 bg-danger/10 border border-danger/20 rounded-lg">
                <AlertCircle size={18} className="text-danger flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-danger">{error}</p>
                  <button onClick={() => setError('')} className="text-xs text-text-muted hover:text-text-primary mt-1">Dismiss</button>
                </div>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!file}
              loading={uploading}
              size="lg"
              fullWidth
            >
              Analyse Resume →
            </Button>
          </div>
        )}
      </div>
    </AppLayout>
  );
};
