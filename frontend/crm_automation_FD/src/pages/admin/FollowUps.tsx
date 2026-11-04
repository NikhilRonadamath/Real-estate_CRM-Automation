import { useEffect, useState } from "react";

import {
  createRecoveryJobs,
  getRecoveryJobs,
  getRecoveryPreview,
  type EligibleLead,
  type RecoveryJob,
} from "../../services/recoveryApi";

export default function FollowUps() {
  const [leads, setLeads] = useState<EligibleLead[]>([]);
  const [jobs, setJobs] = useState<RecoveryJob[]>([]);

  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadData() {
    try {
      setError("");

      const [preview, recoveryJobs] = await Promise.all([
        getRecoveryPreview(),
        getRecoveryJobs(),
      ]);

      setLeads(preview.eligible_leads);
      setJobs(recoveryJobs);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleCreateJobs() {
    try {
      setCreating(true);
      setError("");
      setNotice("");

      const result = await createRecoveryJobs();

      setNotice(
        `${result.created_count} jobs created, ` +
        `${result.existing_count} already existed, ` +
        `${result.skipped_count} leads skipped.`
      );

      await loadData();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to create jobs"
      );
    } finally {
      setCreating(false);
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">Loading recovery data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Recovery Follow-ups
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Review eligible leads and manage recovery job previews.
          </p>
        </div>

        <button
          onClick={handleCreateJobs}
          disabled={creating || leads.length === 0}
          className="rounded-lg bg-blue-600 px-5 py-2.5
            text-sm font-semibold text-white hover:bg-blue-700
            disabled:cursor-not-allowed disabled:opacity-50"
        >
          {creating ? "Creating..." : "Create Recovery Jobs"}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {notice && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">
          {notice}
        </div>
      )}

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
        <p className="text-sm font-semibold text-amber-800">
          Dry-run mode
        </p>
        <p className="mt-1 text-sm text-amber-700">
          These jobs are only saved as previews. No WhatsApp or email
          messages are sent.
        </p>
      </div>

      {/* Eligible leads */}
      <section className="rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900">
            Eligible Leads ({leads.length})
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Leads that currently pass the recovery policy.
          </p>
        </div>

        {leads.length === 0 ? (
          <p className="p-5 text-sm text-gray-500">
            No eligible leads at the moment.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="px-5 py-3">Lead</th>
                  <th className="px-5 py-3">Lead ID</th>
                  <th className="px-5 py-3">Channel</th>
                  <th className="px-5 py-3">Attempts</th>
                  <th className="px-5 py-3">Eligibility</th>
                </tr>
              </thead>

              <tbody>
                {leads.map((lead) => (
                  <tr key={lead.lead_id} className="border-t">
                    <td className="px-5 py-3 font-medium text-gray-900">
                      {lead.name}
                    </td>
                    <td className="px-5 py-3 text-gray-500">
                      {lead.lead_id}
                    </td>
                    <td className="px-5 py-3 capitalize">
                      {lead.channel ?? "Not set"}
                    </td>
                    <td className="px-5 py-3">
                      {lead.recovery_attempts}
                    </td>
                    <td className="px-5 py-3">
                      <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                        Eligible
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Recovery jobs */}
      <section className="rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 p-5">
          <h2 className="font-semibold text-gray-900">
            Recovery Jobs ({jobs.length})
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Job records stored in Firestore.
          </p>
        </div>

        {jobs.length === 0 ? (
          <p className="p-5 text-sm text-gray-500">
            No recovery jobs have been created yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="px-5 py-3">Job ID</th>
                  <th className="px-5 py-3">Lead</th>
                  <th className="px-5 py-3">Channel</th>
                  <th className="px-5 py-3">Attempt</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>

              <tbody>
                {jobs.map((job) => (
                  <tr key={job.job_id} className="border-t">
                    <td className="px-5 py-3 font-medium text-gray-900">
                      {job.job_id}
                    </td>
                    <td className="px-5 py-3">{job.lead_name}</td>
                    <td className="px-5 py-3 capitalize">
                      {job.channel}
                    </td>
                    <td className="px-5 py-3">
                      {job.attempt_number}
                    </td>
                    <td className="px-5 py-3">
                      <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                        {job.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-gray-500">
                      {job.created_at
                        ? new Date(job.created_at).toLocaleString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="flex justify-end">
        <button
          onClick={loadData}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}