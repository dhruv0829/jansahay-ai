import React, { useState, useEffect } from 'react';
import { 
  FileText, Upload, CheckCircle2, AlertTriangle, Trash2, 
  RefreshCw, ShieldCheck, ArrowRight, Sparkles, FileSpreadsheet, Lock
} from 'lucide-react';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { SchemeCard } from '../components/SchemeCard';

export const DocumentCenterPage = () => {
  const { t, language } = useLanguage();
  const { user } = useAuth();
  
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Review modal state
  const [reviewDoc, setReviewDoc] = useState(null);
  const [formData, setFormData] = useState({});
  const [confirming, setConfirming] = useState(false);
  const [freshRecommendations, setFreshRecommendations] = useState([]);
  const [confirmationExplanation, setConfirmationExplanation] = useState('');

  const docTypes = [
    { value: 'Income Certificate', label: language === 'hi' ? 'वार्षिक आय प्रमाण पत्र' : language === 'mr' ? 'वार्षिक उत्पन्न प्रमाणपत्र' : 'Income Certificate' },
    { value: 'Caste Certificate', label: language === 'hi' ? 'जाति प्रमाण पत्र' : language === 'mr' ? 'जात प्रमाणपत्र' : 'Caste Certificate' },
    { value: 'Land Record / Khatauni', label: language === 'hi' ? 'भूमि अभिलेख / 7/12 खतौनी' : language === 'mr' ? '७/१२ जमीन उतारा' : 'Land Record / 7/12 Extract' },
    { value: 'Ration Card', label: language === 'hi' ? 'राशन कार्ड (बीपीएल / प्राथमिकता)' : language === 'mr' ? 'रेशन कार्ड (बीपीएल)' : 'Ration Card' },
  ];

  const [selectedType, setSelectedType] = useState('Income Certificate');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getUserDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
      setError('Unable to load documents. Please ensure you are signed in.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10 MB limit.');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccessMsg(null);
      const res = await api.uploadDocument(file, selectedType);
      
      // Open review modal with extracted values
      setReviewDoc(res);
      setFormData(res.extracted_fields || {});
      setSuccessMsg(res.message);
      
      // Reload list
      await loadDocuments();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to upload and process document.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleConfirmReview = async () => {
    if (!reviewDoc) return;
    try {
      setConfirming(true);
      setError(null);
      const res = await api.confirmDocumentData(reviewDoc.id, formData);
      setSuccessMsg(res.message);
      setConfirmationExplanation(res.explanation);
      setFreshRecommendations(res.recommendations || []);
      setReviewDoc(null);
      await loadDocuments();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to confirm document values.');
    } finally {
      setConfirming(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to permanently delete this document and its private storage file?')) {
      return;
    }
    try {
      await api.deleteDocument(docId);
      setSuccessMsg('Document purged permanently.');
      await loadDocuments();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to delete document.');
    }
  };

  const d = t.documentCenter || {};

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-100 text-emerald-700 rounded-xl">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">{d.title || "Civic Document Center & OCR"}</h1>
            <p className="text-slate-600 mt-1">{d.subtitle || "Upload certificates to verify eligibility with confidence."}</p>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-white border-2 border-dashed border-emerald-300 rounded-2xl p-6 sm:p-8 text-center bg-emerald-50/20 shadow-sm">
        <div className="max-w-xl mx-auto space-y-4">
          <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto">
            {uploading ? <RefreshCw className="w-6 h-6 animate-spin" /> : <Upload className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-800">{d.uploadTitle || "Upload Document for Verification"}</h3>
            <p className="text-sm text-slate-500 mt-1">{d.uploadDesc || "Supports Income, Caste, Land Records (7/12), Ration Card. Max 10MB."}</p>
          </div>

          {/* Type Hint Selector */}
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {docTypes.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setSelectedType(type.value)}
                className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                  selectedType === type.value
                    ? 'bg-emerald-700 text-white border-emerald-700 shadow-sm'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
              >
                {type.label}
              </button>
            ))}
          </div>

          {/* File Input */}
          <div className="pt-3">
            <label className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-700 text-white rounded-xl font-medium cursor-pointer hover:bg-emerald-800 transition shadow-sm">
              <Upload className="w-4 h-4" />
              <span>{uploading ? (d.processing || "Processing OCR...") : "Choose File to Upload"}</span>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>
          
          <div className="flex items-center justify-center gap-2 text-xs text-slate-500 pt-1">
            <Lock className="w-3.5 h-3.5" />
            <span>Uploads are stored by JanSahay for text extraction and eligibility review. Review detected values before confirming them.</span>
          </div>
        </div>
      </div>

      {/* Review Modal if document just uploaded or selected */}
      {reviewDoc && (
        <div className="bg-white border-2 border-emerald-500 rounded-2xl p-6 shadow-md space-y-4">
          <div className="flex items-center justify-between border-b pb-3">
            <div className="flex items-center gap-2 text-emerald-700">
              <Sparkles className="w-5 h-5" />
              <h3 className="font-semibold text-lg text-slate-900">{d.reviewTitle || "Review & Confirm Extracted Values"}</h3>
            </div>
            <div className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-semibold">
              {d.confidence || "Extraction Confidence"}: {Math.round((reviewDoc.confidence_score || 0.85) * 100)}%
            </div>
          </div>

          <p className="text-sm text-slate-600">
            {d.reviewDesc || "Please review and adjust any detected fields before applying them to your profile."}
          </p>

          {/* Uncertainty Alerts */}
          {reviewDoc.uncertainty_indicators && reviewDoc.uncertainty_indicators.length > 0 && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs space-y-1">
              <div className="font-medium flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span>Notice on automated extraction:</span>
              </div>
              <ul className="list-disc list-inside">
                {reviewDoc.uncertainty_indicators.map((u, i) => (
                  <li key={i}>{u}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Form Fields for Confirmation */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Annual Household Income (₹)</label>
              <input
                type="number"
                value={formData.annual_income || ''}
                onChange={(e) => setFormData({ ...formData, annual_income: e.target.value })}
                placeholder="e.g. 180000"
                className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Social Category</label>
              <select
                value={formData.social_category || 'General'}
                onChange={(e) => setFormData({ ...formData, social_category: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none bg-white"
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Landholding (Acres)</label>
              <input
                type="number"
                step="0.1"
                value={formData.landholding_acres || ''}
                onChange={(e) => setFormData({ ...formData, landholding_acres: e.target.value })}
                placeholder="e.g. 2.5"
                className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Residential State</label>
              <input
                type="text"
                value={formData.state || ''}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="e.g. Maharashtra"
                className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t">
            <button
              type="button"
              onClick={() => setReviewDoc(null)}
              className="px-4 py-2 border rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirmReview}
              disabled={confirming}
              className="px-5 py-2 bg-emerald-700 text-white rounded-lg text-sm font-medium hover:bg-emerald-800 transition flex items-center gap-2 shadow-sm"
            >
              {confirming ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              <span>{d.confirmButton || "Confirm & Update Profile"}</span>
            </button>
          </div>
        </div>
      )}

      {/* Fresh Recommendations from Newly Confirmed Profile */}
      {freshRecommendations.length > 0 && (
        <div className="bg-emerald-50/60 border border-emerald-200 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-emerald-800">
            <Sparkles className="w-5 h-5" />
            <h3 className="font-bold text-lg">Newly Verified Recommendations</h3>
          </div>
          {confirmationExplanation && (
            <p className="text-sm text-emerald-900 bg-white/70 p-3 rounded-xl border border-emerald-200">
              {confirmationExplanation}
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {freshRecommendations.map((rec) => (
              <SchemeCard key={rec.scheme.id} scheme={rec.scheme} recommendation={rec} />
            ))}
          </div>
        </div>
      )}

      {/* Uploaded Documents List */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <FileText className="w-5 h-5 text-emerald-700" />
          <span>Verified Documents ({documents.length})</span>
        </h3>

        {loading ? (
          <div className="p-8 text-center text-slate-500">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-600" />
            <span>Loading documents...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-8 bg-white border border-slate-200 rounded-2xl text-center text-slate-500">
            <FileSpreadsheet className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm">{d.noDocuments || "No documents uploaded yet. Upload a certificate above to start automatic profile verification."}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-white border rounded-2xl p-5 shadow-sm space-y-3 relative group hover:border-emerald-300 transition">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2.5 bg-emerald-50 text-emerald-700 rounded-xl">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-900 text-sm">{doc.document_type}</h4>
                      <p className="text-xs text-slate-400 truncate max-w-[170px]">{doc.original_filename}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    title={d.deleteButton || "Delete Permanently"}
                    className="text-slate-400 hover:text-red-600 p-1.5 transition rounded-lg hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-100">
                  <span className="text-slate-500">Confidence: {Math.round((doc.confidence_score || 0.85) * 100)}%</span>
                  {doc.is_verified_by_user ? (
                    <span className="flex items-center gap-1 text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                    </span>
                  ) : (
                    <span className="text-amber-700 font-medium bg-amber-50 px-2 py-0.5 rounded-full">
                      Pending Review
                    </span>
                  )}
                </div>

                {/* Extracted Fields Summary */}
                {doc.verified_fields && Object.keys(doc.verified_fields).length > 0 && (
                  <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl space-y-0.5">
                    {doc.verified_fields.annual_income && (
                      <div>Income: <strong>₹{Number(doc.verified_fields.annual_income).toLocaleString('en-IN')}</strong></div>
                    )}
                    {doc.verified_fields.social_category && (
                      <div>Category: <strong>{doc.verified_fields.social_category}</strong></div>
                    )}
                    {doc.verified_fields.landholding_acres && (
                      <div>Landholding: <strong>{doc.verified_fields.landholding_acres} Acres</strong></div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
