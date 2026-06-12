import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  FileText,
  Filter,
  Flag,
  Mail,
  MessageSquareText,
  Search,
  ShieldAlert,
  Ticket,
} from "lucide-react";
import { fetchAgentActivity } from "../api/api";
import TopNavbar from "../components/TopNavbar";

const actionConfig = {
  escalate_to_human: {
    label: "Escalate to Human",
    icon: ShieldAlert,
    card: "border-red-200 bg-red-50/60",
    iconBox: "bg-red-100 text-red-700",
    badge: "border-red-200 bg-red-100 text-red-700",
    line: "bg-red-200",
  },
  create_internal_ticket: {
    label: "Create Internal Ticket",
    icon: Ticket,
    card: "border-blue-200 bg-blue-50/60",
    iconBox: "bg-blue-100 text-blue-700",
    badge: "border-blue-200 bg-blue-100 text-blue-700",
    line: "bg-blue-200",
  },
  draft_reply: {
    label: "Draft Reply",
    icon: MessageSquareText,
    card: "border-green-200 bg-green-50/60",
    iconBox: "bg-green-100 text-green-700",
    badge: "border-green-200 bg-green-100 text-green-700",
    line: "bg-green-200",
  },
  ignore: {
    label: "Ignore",
    icon: FileText,
    card: "border-gray-200 bg-gray-50",
    iconBox: "bg-gray-200 text-gray-700",
    badge: "border-gray-200 bg-gray-100 text-gray-700",
    line: "bg-gray-200",
  },
  flag_for_legal: {
    label: "Flag for Legal",
    icon: Flag,
    card: "border-orange-200 bg-orange-50/70",
    iconBox: "bg-orange-100 text-orange-700",
    badge: "border-orange-200 bg-orange-100 text-orange-700",
    line: "bg-orange-200",
  },
};

const fallbackConfig = {
  label: "Agent Action",
  icon: Mail,
  card: "border-slate-200 bg-white",
  iconBox: "bg-slate-100 text-slate-600",
  badge: "border-slate-200 bg-slate-100 text-slate-700",
  line: "bg-slate-200",
};

function formatActionType(actionType) {
  return (
    actionConfig[actionType]?.label ||
    actionType
      ?.split("_")
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ") ||
    "Unknown Action"
  );
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

function getUniqueActionTypes(items) {
  return [...new Set(items.map((item) => item.action_type).filter(Boolean))].sort();
}

export default function AgentActivity() {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [actionType, setActionType] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadActivity() {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchAgentActivity();
        if (!cancelled) setActivities(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail?.message ||
              err?.message ||
              "Failed to load agent activity"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadActivity();
    return () => {
      cancelled = true;
    };
  }, []);

  const actionTypes = useMemo(() => getUniqueActionTypes(activities), [activities]);

  const visibleActivities = useMemo(() => {
    const query = search.trim().toLowerCase();

    return activities
      .filter((activity) => {
        const matchesSearch =
          !query || activity.action_type?.toLowerCase().includes(query);
        const matchesType =
          actionType === "All" || activity.action_type === actionType;

        return matchesSearch && matchesType;
      })
      .sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));
  }, [activities, actionType, search]);

  return (
    <>
      <TopNavbar
        title="Agent Activity"
        subtitle="Autonomous actions, escalations, and response decisions"
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
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-base font-semibold text-slate-900">
                    Recent Agent Actions
                  </h2>
                  <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
                    {loading ? "..." : visibleActivities.length}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-500">
                  {loading
                    ? "Loading operations timeline"
                    : `${visibleActivities.length} of ${activities.length} events shown`}
                </p>
              </div>

              <div className="grid gap-3 md:grid-cols-[minmax(240px,1fr)_220px] xl:w-[560px]">
                <label className="relative block">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search action type"
                    className="h-10 w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  />
                </label>

                <label className="relative block">
                  <Filter className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <select
                    value={actionType}
                    onChange={(event) => setActionType(event.target.value)}
                    className="h-10 w-full appearance-none rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  >
                    <option value="All">All actions</option>
                    {actionTypes.map((item) => (
                      <option key={item} value={item}>
                        {formatActionType(item)}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
          </div>

          <div className="px-4 py-5 sm:px-5">
            {loading && (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="h-11 w-11 shrink-0 animate-pulse rounded-xl bg-slate-100" />
                    <div className="flex-1 rounded-xl border border-slate-200 bg-white p-4">
                      <div className="h-4 w-44 animate-pulse rounded bg-slate-100" />
                      <div className="mt-3 h-4 w-full animate-pulse rounded bg-slate-100" />
                      <div className="mt-3 h-4 w-64 animate-pulse rounded bg-slate-100" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && visibleActivities.length > 0 && (
              <div className="relative space-y-4">
                {visibleActivities.map((activity, index) => {
                  const config = actionConfig[activity.action_type] || fallbackConfig;
                  const Icon = config.icon;

                  return (
                    <article
                      key={`${activity.email_id}-${activity.timestamp}-${index}`}
                      className="relative flex gap-4"
                    >
                      {index < visibleActivities.length - 1 && (
                        <div
                          className={`absolute left-[21px] top-12 h-[calc(100%+1rem)] w-px ${config.line}`}
                        />
                      )}

                      <div
                        className={`z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${config.iconBox}`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>

                      <div
                        className={`min-w-0 flex-1 rounded-xl border p-4 shadow-sm ${config.card}`}
                      >
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <span
                                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${config.badge}`}
                              >
                                {formatActionType(activity.action_type)}
                              </span>
                              <span className="text-xs font-medium text-slate-500">
                                {formatTimestamp(activity.timestamp)}
                              </span>
                            </div>
                            <p className="mt-3 text-sm font-medium text-slate-900">
                              {activity.reason || "No reason provided"}
                            </p>
                          </div>

                          <div className="flex shrink-0 items-center gap-2 rounded-lg border border-slate-200 bg-white/80 px-3 py-2 text-xs font-medium text-slate-600">
                            <Mail className="h-3.5 w-3.5 text-slate-400" />
                            <span className="max-w-[180px] truncate">
                              {activity.email_id || "No email ID"}
                            </span>
                          </div>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {!loading && visibleActivities.length === 0 && (
              <div className="flex flex-col items-center justify-center px-5 py-14 text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                  <Search className="h-5 w-5" />
                </div>
                <p className="mt-3 text-sm font-medium text-slate-900">
                  No agent actions found
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Adjust search or filters to widen the activity timeline.
                </p>
              </div>
            )}
          </div>
        </section>
      </div>
    </>
  );
}
