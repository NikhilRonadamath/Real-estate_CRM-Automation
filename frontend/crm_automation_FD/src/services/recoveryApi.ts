const API_BASE_URL = "http://127.0.0.1:8000/api";

export interface EligibleLead {
  lead_id: string;
  name: string;
  channel: string | null;
  eligible: boolean;
  reasons: string[];
  recovery_attempts: number;
}

export interface RecoveryJob {
  job_id: string;
  lead_id: string;
  lead_name: string;
  channel: string;
  attempt_number: number;
  retry_count: number;
  status: string;
  mode: string;
  scheduled_at: string | null;
  executed_at: string | null;
  last_error: string | null;
  created_at: string;
  created?: boolean;
}

export interface RecoveryPreview {
  success: boolean;
  mode: string;
  messages_sent: number;
  total_leads_scanned: number;
  eligible_count: number;
  blocked_count: number;
  eligible_leads: EligibleLead[];
  blocked_leads: EligibleLead[];
}

export interface CreateJobsResponse {
  success: boolean;
  mode: string;
  messages_sent: number;
  created_count: number;
  existing_count: number;
  skipped_count: number;
  created_jobs: RecoveryJob[];
  existing_jobs: RecoveryJob[];
}

export async function getRecoveryPreview(): Promise<RecoveryPreview> {
  const response = await fetch(`${API_BASE_URL}/recovery/preview`);

  if (!response.ok) {
    throw new Error("Unable to fetch recovery preview");
  }

  return response.json();
}

export async function createRecoveryJobs(): Promise<CreateJobsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/recovery/jobs/dry-run`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error("Unable to create recovery jobs");
  }

  return response.json();
}

export async function getRecoveryJobs(): Promise<RecoveryJob[]> {
  const response = await fetch(`${API_BASE_URL}/recovery/jobs`);

  if (!response.ok) {
    throw new Error("Unable to fetch recovery jobs");
  }

  const data = await response.json();
  return data.jobs;
}