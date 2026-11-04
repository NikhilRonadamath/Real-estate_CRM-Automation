import { useState, type ChangeEvent, type FormEvent } from 'react'

import {
  Building2,
  User,
  CalendarDays,
  CheckCircle2,
  ArrowRight,
  Loader2,
  Home,
  ShieldCheck,
  RotateCcw,
} from 'lucide-react'

import api from '../services/api'
import FormField from '../components/FormField'
import FormSection from '../components/FormSection'

import type {
  LeadFormData,
  LeadResponse,
} from '../types/lead'

const initialForm: LeadFormData = {
  name: '',
  email: '',
  phone: '',
  property_type: '',
  location: '',
  estimated_value: undefined,
  selling_timeline: '',
  motivation: '',
}

const inputClass =
  'w-full rounded-lg border border-slate-200 bg-white px-3.5 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-slate-900 focus:ring-2 focus:ring-slate-100'

export default function LeadForm() {
  const [form, setForm] = useState<LeadFormData>(initialForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState<LeadResponse | null>(null)

  const handleChange = (
    event: ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value } = event.target

    setForm((previous) => ({
      ...previous,
      [name]:
        name === 'estimated_value'
          ? value === ''
            ? undefined
            : Number(value)
          : value,
    }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setError('')
    setSuccess(null)

    if (form.phone.replace(/\D/g, '').length < 10) {
      setError('Please enter a valid phone number.')
      return
    }

    if (
      form.estimated_value !== undefined &&
      form.estimated_value <= 0
    ) {
      setError('Property value must be greater than zero.')
      return
    }

    setLoading(true)

    try {
      const response = await api.post<LeadResponse>(
        '/api/leads/',
        form,
      )

      setSuccess(response.data)
      setForm({ ...initialForm })
    } catch (err: unknown) {
      const backendError =
        typeof err === 'object' && err !== null && 'response' in err
          ? (err as { response?: { data?: { detail?: unknown } } }).response?.data?.detail
          : undefined

      setError(
        typeof backendError === 'string'
          ? backendError
          : 'Unable to submit your enquiry. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setForm({ ...initialForm })
    setError('')
    setSuccess(null)
  }

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
        <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
            <CheckCircle2 size={34} className="text-green-600" />
          </div>

          <h1 className="text-2xl font-bold text-slate-900">
            Enquiry Submitted!
          </h1>

          <p className="mt-3 text-sm leading-6 text-slate-500">
            Thank you for sharing your property details.
            Your information has been registered successfully.
          </p>

          <div className="mt-6 rounded-lg bg-slate-50 p-4 text-left">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Lead Reference ID
            </p>
            <p className="mt-2 break-all font-mono text-sm font-semibold text-slate-800">
              {success.lead_id}
            </p>
          </div>

          <button
            onClick={handleReset}
            className="mt-7 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
          >
            <RotateCcw size={16} />
            Submit Another Enquiry
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 sm:py-12">
      <div className="mx-auto max-w-3xl">
        <header className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Building2 size={23} />
            </div>
            <div>
              <h2 className="font-bold text-slate-900">EstateConnect</h2>
              <p className="text-xs text-slate-500">Property Enquiry Portal</p>
            </div>
          </div>

          <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500">
            Seller Registration
          </span>
        </header>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-6 py-7 sm:px-9">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600">
              <Home size={14} />
              Real Estate Services
            </div>

            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Tell us about your property
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500">
              Share a few details about your property and
              selling plans. Our team will use this information
              to understand your requirements.
            </p>

            <div className="mt-5 flex items-center gap-2 text-xs text-slate-500">
              <ShieldCheck size={15} className="text-green-600" />
              Your information is handled securely.
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-9 px-6 py-8 sm:px-9"
          >
            <FormSection
              title="Personal Information"
              description="Basic details about the property owner."
              icon={<User size={19} />}
            >
              <FormField label="Full Name" required>
                <input
                  className={inputClass}
                  name="name"
                  placeholder="Enter your full name"
                  value={form.name}
                  onChange={handleChange}
                  minLength={2}
                  maxLength={100}
                  required
                />
              </FormField>

              <FormField label="Phone Number" required>
                <input
                  className={inputClass}
                  name="phone"
                  type="tel"
                  placeholder="+91 9876543210"
                  value={form.phone}
                  onChange={handleChange}
                  maxLength={20}
                  required
                />
              </FormField>

              <FormField label="Email Address" required fullWidth>
                <input
                  className={inputClass}
                  name="email"
                  type="email"
                  placeholder="example@email.com"
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </FormField>
            </FormSection>

            <FormSection
              title="Property Information"
              description="Tell us about the property you are planning to sell."
              icon={<Building2 size={19} />}
            >
              <FormField label="Property Type" required>
                <select
                  className={inputClass}
                  name="property_type"
                  value={form.property_type}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select property type</option>
                  <option value="apartment">Apartment</option>
                  <option value="independent_house">Independent House</option>
                  <option value="villa">Villa</option>
                  <option value="land">Land / Plot</option>
                  <option value="commercial">Commercial Property</option>
                </select>
              </FormField>

              <FormField label="Property Location" required>
                <input
                  className={inputClass}
                  name="location"
                  placeholder="City / Area"
                  value={form.location}
                  onChange={handleChange}
                  required
                />
              </FormField>

              <FormField
                label="Estimated Property Value (INR)"
                fullWidth
              >
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-sm text-slate-400">
                    ₹
                  </span>
                  <input
                    className={`${inputClass} pl-8`}
                    name="estimated_value"
                    type="number"
                    min="1"
                    placeholder="8500000"
                    value={form.estimated_value ?? ''}
                    onChange={handleChange}
                  />
                </div>

                <p className="text-xs text-slate-400">
                  Enter the approximate property value in rupees.
                </p>
              </FormField>
            </FormSection>

            <FormSection
              title="Selling Information"
              description="Understand your plans and motivation."
              icon={<CalendarDays size={19} />}
            >
              <FormField label="Selling Timeline" fullWidth>
                <select
                  className={inputClass}
                  name="selling_timeline"
                  value={form.selling_timeline}
                  onChange={handleChange}
                >
                  <option value="">Select your selling timeline</option>
                  <option value="immediately">Immediately</option>
                  <option value="1-3_months">Within 1–3 Months</option>
                  <option value="3-6_months">Within 3–6 Months</option>
                  <option value="6-12_months">Within 6–12 Months</option>
                  <option value="more_than_1_year">After 1 Year</option>
                  <option value="exploring">Just Exploring</option>
                </select>
              </FormField>

              <FormField label="Why are you planning to sell?" fullWidth>
                <textarea
                  className={`${inputClass} resize-none`}
                  name="motivation"
                  placeholder="For example: Relocation, financial requirements, investment change, etc."
                  value={form.motivation}
                  onChange={handleChange}
                  rows={4}
                  maxLength={1000}
                />

                <p className="text-right text-xs text-slate-400">
                  {form.motivation.length}/1000
                </p>
              </FormField>
            </FormSection>

            {error && (
              <div
                role="alert"
                className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700"
              >
                {error}
              </div>
            )}

            <div className="border-t border-slate-100 pt-6">
              <p className="mb-5 text-xs leading-5 text-slate-400">
                By submitting this form, you confirm that
                the information provided is accurate and that
                you are authorized to share these property details.
                This submission does not itself authorize automated
                marketing messages.
              </p>

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Submitting Enquiry...
                  </>
                ) : (
                  <>
                    Submit Property Enquiry
                    <ArrowRight size={17} />
                  </>
                )}
              </button>

              <p className="mt-4 text-center text-xs text-slate-400">
                Required fields are marked with an asterisk (*).
              </p>
            </div>
          </form>
        </div>

        <footer className="py-7 text-center text-xs text-slate-400">
          EstateConnect · Property Enquiry Portal
          <br />
          Powered by AI Lead Recovery Engine
        </footer>
      </div>
    </main>
  )
}
