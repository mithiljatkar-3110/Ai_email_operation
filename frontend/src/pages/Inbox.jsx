import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Filter, Inbox as InboxIcon, Search } from "lucide-react";
import { fetchInbox } from "../api/api";
import TopNavbar from "../components/TopNavbar";

const urgencyStyles = {
  Critical: "border-red-200 bg-red-50 text-red-700",
  High: "border-orange-200 bg-orange-50 text-orange-700",
  Medium: "border-yellow-200 bg-yellow-50 text-yellow-800",
  Low: "border-green-200 bg-green-50 text-green-700",
};

const categoryStyles = {
  Spam: "border-gray-200 bg-gray-100 text-gray-700",
  Complaint: "border-orange-200 bg-orange-50 text-orange-700",
  Compliance: "border-blue-200 bg-blue-50 text-blue-700",
  Legal: "border-red-200 bg-red-50 text-red-700",
  Inquiry: "border-green-200 bg-green-50 text-green-700",
};

function Badge({ children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${className}`}
    >
      {children || "Uncategorized"}
    </span>
  );
}

function formatConfidence(value) {
  if (value == null || Number.isNaN(Number(value))) return "-";
  return `${Math.round(Number(value) * 100)}%`;
}

function formatTimestamp(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getUniqueValues(items, key) {
  return [...new Set(items.map((item) => item[key]).filter(Boolean))].sort();
}

export default function Inbox() {
  const navigate = useNavigate();
  const [emails, setEmails] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [urgency, setUrgency] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadInbox() {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchInbox();
        if (!cancelled) setEmails(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail?.message ||
              err?.message ||
              "Failed to load inbox"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadInbox();
    return () => {
      cancelled = true;
    };
  }, []);

  const categories = useMemo(() => getUniqueValues(emails, "category"), [emails]);
  const urgencies = useMemo(() => getUniqueValues(emails, "urgency"), [emails]);

  const visibleEmails = useMemo(() => {
    const query = search.trim().toLowerCase();

    return emails
      .filter((email) => {
        const matchesSearch =
          !query ||
          email.sender?.toLowerCase().includes(query) ||
          email.subject?.toLowerCase().includes(query);
        const matchesCategory = category === "All" || email.category === category;
        const matchesUrgency = urgency === "All" || email.urgency === urgency;

        return matchesSearch && matchesCategory && matchesUrgency;
      })
      .sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));
  }, [emails, search, category, urgency]);

  function openThread(email) {
    const threadId = email.thread_id || email.threadId || email.email_id;
    if (threadId) navigate(`/thread/${threadId}`);
  }

  return (
    <>
      <TopNavbar
        title="Inbox"
        subtitle="Search, filter, and triage inbound customer conversations"
      />

      <div className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-4 py-4 sm:px-5">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <InboxIcon className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-slate-900">
                    Email Queue
                  </h2>
                  <p className="text-sm text-slate-500">
                    {loading
                      ? "Loading inbound messages"
                      : `${visibleEmails.length} of ${emails.length} messages shown`}
                  </p>
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px_180px] xl:w-[720px]">
                <label className="relative block">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search sender or subject"
                    className="h-10 w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  />
                </label>

                <label className="relative block">
                  <Filter className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <select
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                    className="h-10 w-full appearance-none rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  >
                    <option value="All">All categories</option>
                    {categories.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>

                <select
                  value={urgency}
                  onChange={(event) => setUrgency(event.target.value)}
                  className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                >
                  <option value="All">All urgencies</option>
                  {urgencies.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-[980px] w-full divide-y divide-slate-200 text-left">
              <thead className="bg-slate-50">
                <tr>
                  {[
                    "Sender",
                    "Subject",
                    "Category",
                    "Urgency",
                    "Confidence",
                    "Status",
                    "Timestamp",
                  ].map((heading) => (
                    <th
                      key={heading}
                      className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {loading &&
                  Array.from({ length: 6 }).map((_, index) => (
                    <tr key={index} className="animate-pulse">
                      {Array.from({ length: 7 }).map((__, cellIndex) => (
                        <td key={cellIndex} className="px-5 py-4">
                          <div className="h-4 rounded bg-slate-100" />
                        </td>
                      ))}
                    </tr>
                  ))}

                {!loading &&
                  visibleEmails.map((email) => (
                    <tr
                      key={email.email_id}
                      onClick={() => openThread(email)}
                      className="cursor-pointer transition hover:bg-indigo-50/50"
                    >
                      <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-900">
                        {email.sender || "-"}
                      </td>
                      <td className="max-w-[340px] px-5 py-4 text-sm text-slate-700">
                        <div className="truncate" title={email.subject}>
                          {email.subject || "(No subject)"}
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-5 py-4">
                        <Badge
                          className={
                            categoryStyles[email.category] ||
                            "border-slate-200 bg-slate-50 text-slate-600"
                          }
                        >
                          {email.category}
                        </Badge>
                      </td>
                      <td className="whitespace-nowrap px-5 py-4">
                        <Badge
                          className={
                            urgencyStyles[email.urgency] ||
                            "border-slate-200 bg-slate-50 text-slate-600"
                          }
                        >
                          {email.urgency}
                        </Badge>
                      </td>
                      <td className="whitespace-nowrap px-5 py-4 text-sm font-medium text-slate-700">
                        {formatConfidence(email.confidence)}
                      </td>
                      <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                        {email.status || "-"}
                      </td>
                      <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-500">
                        {formatTimestamp(email.timestamp)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {!loading && visibleEmails.length === 0 && (
            <div className="flex flex-col items-center justify-center px-5 py-14 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                <Search className="h-5 w-5" />
              </div>
              <p className="mt-3 text-sm font-medium text-slate-900">
                No emails found
              </p>
              <p className="mt-1 text-sm text-slate-500">
                Adjust search or filters to widen the inbox view.
              </p>
            </div>
          )}
        </section>
      </div>
    </>
  );
}
