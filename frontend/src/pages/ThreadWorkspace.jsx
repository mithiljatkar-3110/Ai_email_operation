import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowDown,
  Brain,
  FileText,
  Gauge,
  Mail,
  MessageSquareText,
  ShieldAlert,
  Sparkles,
  Ticket,
  Search,
} from "lucide-react";
import { fetchThreadWorkspace } from "../api/api";
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

const actionStyles = {
  escalate_to_human: {
    label: "Escalate to Human",
    icon: ShieldAlert,
    badge: "border-red-200 bg-red-50 text-red-700",
    iconBox: "bg-red-100 text-red-700",
  },
  create_internal_ticket: {
    label: "Create Internal Ticket",
    icon: Ticket,
    badge: "border-blue-200 bg-blue-50 text-blue-700",
    iconBox: "bg-blue-100 text-blue-700",
  },
  draft_reply: {
    label: "Draft Reply",
    icon: MessageSquareText,
    badge: "border-green-200 bg-green-50 text-green-700",
    iconBox: "bg-green-100 text-green-700",
  },
  ignore: {
    label: "Ignore",
    icon: FileText,
    badge: "border-gray-200 bg-gray-100 text-gray-700",
    iconBox: "bg-gray-200 text-gray-700",
  },
  flag_for_legal: {
    label: "Flag for Legal",
    icon: ShieldAlert,
    badge: "border-orange-200 bg-orange-50 text-orange-700",
    iconBox: "bg-orange-100 text-orange-700",
  },
  retention_draft_response: {
    label: "Retention Draft Response",
    icon: MessageSquareText,
    badge: "border-emerald-200 bg-emerald-50 text-emerald-700",
    iconBox: "bg-emerald-100 text-emerald-700",
  },
};

function Badge({ children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${className}`}
    >
      {children || "None"}
    </span>
  );
}

function formatActionType(actionType) {
  return (
    actionStyles[actionType]?.label ||
    actionType
      ?.split("_")
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ") ||
    "No Action"
  );
}

function formatPercent(value) {
  if (value == null || Number.isNaN(Number(value))) return "-";
  return `${Math.round(Number(value) * 100)}%`;
}

function formatSentiment(value) {
  if (value == null || Number.isNaN(Number(value))) return "-";
  const score = Number(value);
  if (score > 0.2) return `Positive (${score.toFixed(2)})`;
  if (score < -0.2) return `Negative (${score.toFixed(2)})`;
  return `Neutral (${score.toFixed(2)})`;
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

function extractEscalationReason(trace) {
  const escalationStep = [...trace]
    .reverse()
    .find(
      (step) =>
        step.action?.includes("escalate") ||
        step.observation?.toLowerCase().includes("escalat")
    );

  if (!escalationStep) return "No escalation reason recorded.";

  const reasonMatch = escalationStep.action?.match(/reason=(['"])(.*?)\1/);
  if (reasonMatch?.[2]) return reasonMatch[2];

  return escalationStep.observation || escalationStep.thought;
}

function latestAction(actions) {
  return actions?.[0] || null;
}

export default function ThreadWorkspace() {
  const { threadId } = useParams();
  const [workspace, setWorkspace] = useState(null);
  const [loading, setLoading] = useState(Boolean(threadId));
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspace() {
      if (!threadId) {
        setWorkspace(null);
        setError(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await fetchThreadWorkspace(threadId);
        if (!cancelled) setWorkspace(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail?.message ||
              err?.message ||
              "Failed to load thread workspace"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadWorkspace();
    return () => {
      cancelled = true;
    };
  }, [threadId]);

  const thread = useMemo(() => workspace?.thread || [], [workspace]);
  const classification = workspace?.classification;
  const agentActions = useMemo(() => workspace?.agent_actions || [], [workspace]);
  const reasoningTrace = useMemo(
    () => workspace?.reasoning_trace || [],
    [workspace]
  );

  const decision = useMemo(() => latestAction(agentActions), [agentActions]);
  const escalationReason = useMemo(
    () => extractEscalationReason(reasoningTrace),
    [reasoningTrace]
  );

  return (
    <>
      <TopNavbar
        title="Thread Workspace"
        subtitle={
          threadId
            ? `Conversation intelligence and agent reasoning for ${threadId}`
            : "Select a customer thread to inspect conversation context and AI decisions"
        }
      />

      <div className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        {!threadId ? (
          <section className="flex min-h-[520px] items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
            <div className="max-w-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <Search className="h-6 w-6" />
              </div>
              <h2 className="mt-5 text-lg font-semibold text-slate-900">
                Select a Thread
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Open a conversation from the inbox to view full email history,
                classification, agent decisions, reasoning, and saved actions.
              </p>
              <Link
                to="/inbox"
                className="mt-5 inline-flex h-10 items-center justify-center rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
              >
                Go to Inbox
              </Link>
            </div>
          </section>
        ) : loading ? (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,65fr)_minmax(320px,35fr)]">
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                >
                  <div className="h-4 w-48 animate-pulse rounded bg-slate-100" />
                  <div className="mt-4 h-4 w-full animate-pulse rounded bg-slate-100" />
                  <div className="mt-3 h-4 w-4/5 animate-pulse rounded bg-slate-100" />
                </div>
              ))}
            </div>
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                >
                  <div className="h-4 w-36 animate-pulse rounded bg-slate-100" />
                  <div className="mt-4 h-16 animate-pulse rounded bg-slate-100" />
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,65fr)_minmax(320px,35fr)]">
            <section className="min-w-0 rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 px-5 py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">
                      Email Thread History
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                      Chronological customer conversation context
                    </p>
                  </div>
                  <Badge className="border-indigo-200 bg-indigo-50 text-indigo-700">
                    {thread.length} messages
                  </Badge>
                </div>
              </div>

              <div className="space-y-4 p-5">
                {thread.length === 0 && (
                  <div className="flex flex-col items-center justify-center px-5 py-16 text-center">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                      <Mail className="h-5 w-5" />
                    </div>
                    <p className="mt-3 text-sm font-medium text-slate-900">
                      No messages in this thread
                    </p>
                  </div>
                )}

                {thread.map((email, index) => (
                  <article
                    key={email.email_id || index}
                    className="rounded-xl border border-slate-200 bg-slate-50/60 p-5"
                  >
                    <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-indigo-600 shadow-sm">
                            <Mail className="h-4 w-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-slate-900">
                              {email.sender || "Unknown sender"}
                            </p>
                            <p className="text-xs text-slate-500">
                              {formatTimestamp(email.timestamp)}
                            </p>
                          </div>
                        </div>
                      </div>
                      <Badge className="border-slate-200 bg-white text-slate-600">
                        {email.status}
                      </Badge>
                    </div>

                    <h3 className="mt-4 text-base font-semibold text-slate-900">
                      {email.subject || "(No subject)"}
                    </h3>
                    <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                      {email.body || "(Empty message)"}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <aside className="min-w-0 space-y-5">
              <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <Gauge className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">
                      Classification
                    </h2>
                    <p className="text-sm text-slate-500">Latest model assessment</p>
                  </div>
                </div>

                {classification ? (
                  <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <p className="text-xs font-medium text-slate-500">Category</p>
                      <div className="mt-2">
                        <Badge
                          className={
                            categoryStyles[classification.category] ||
                            "border-slate-200 bg-white text-slate-700"
                          }
                        >
                          {classification.category}
                        </Badge>
                      </div>
                    </div>
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <p className="text-xs font-medium text-slate-500">Urgency</p>
                      <div className="mt-2">
                        <Badge
                          className={
                            urgencyStyles[classification.urgency] ||
                            "border-slate-200 bg-white text-slate-700"
                          }
                        >
                          {classification.urgency}
                        </Badge>
                      </div>
                    </div>
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <p className="text-xs font-medium text-slate-500">Confidence</p>
                      <p className="mt-2 text-sm font-semibold text-slate-900">
                        {formatPercent(classification.confidence)}
                      </p>
                    </div>
                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <p className="text-xs font-medium text-slate-500">Sentiment</p>
                      <p className="mt-2 text-sm font-semibold text-slate-900">
                        {formatSentiment(classification.sentiment_score)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                    No classification available for this thread.
                  </p>
                )}
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                    <Brain className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">
                      Agent Decision
                    </h2>
                    <p className="text-sm text-slate-500">Persisted final outcome</p>
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p className="text-xs font-medium text-slate-500">Final Action</p>
                    <div className="mt-2">
                      <Badge
                        className={
                          actionStyles[decision?.action_type]?.badge ||
                          "border-slate-200 bg-white text-slate-700"
                        }
                      >
                        {formatActionType(decision?.action_type)}
                      </Badge>
                    </div>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p className="text-xs font-medium text-slate-500">
                      Escalation Reason
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-800">
                      {escalationReason}
                    </p>
                  </div>
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">
                      Reasoning Trace
                    </h2>
                    <p className="text-sm text-slate-500">Thought to action trail</p>
                  </div>
                </div>

                <div className="mt-5 space-y-4">
                  {reasoningTrace.length === 0 && (
                    <p className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                      No reasoning trace has been saved yet.
                    </p>
                  )}

                  {reasoningTrace.map((step, index) => (
                    <article
                      key={`${step.action}-${index}`}
                      className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                    >
                      <p className="text-xs font-semibold uppercase text-slate-500">
                        Step {index + 1}
                      </p>
                      <div className="mt-3 space-y-3">
                        <TraceBlock label="Thought" value={step.thought} />
                        <ArrowDown className="mx-auto h-4 w-4 text-slate-400" />
                        <TraceBlock label="Action" value={step.action} />
                        <ArrowDown className="mx-auto h-4 w-4 text-slate-400" />
                        <TraceBlock label="Observation" value={step.observation} />
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700">
                    <Ticket className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-900">
                      Agent Actions
                    </h2>
                    <p className="text-sm text-slate-500">
                      Tickets, escalations, and drafts
                    </p>
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  {agentActions.length === 0 && (
                    <p className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                      No agent actions recorded for this thread.
                    </p>
                  )}

                  {agentActions.map((action) => {
                    const config = actionStyles[action.action_type] || actionStyles.ignore;
                    const Icon = config.icon;

                    return (
                      <article
                        key={action.action_id}
                        className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${config.iconBox}`}
                          >
                            <Icon className="h-4 w-4" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <Badge className={config.badge}>
                                {formatActionType(action.action_type)}
                              </Badge>
                              <span className="text-xs text-slate-500">
                                {formatTimestamp(action.timestamp)}
                              </span>
                            </div>
                            <p className="mt-2 truncate text-xs text-slate-500">
                              Email ID: {action.email_id}
                            </p>
                            {action.proposed_content && (
                              <p className="mt-3 line-clamp-4 whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-3 text-sm leading-6 text-slate-700">
                                {action.proposed_content}
                              </p>
                            )}
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>
              </section>
            </aside>
          </div>
        )}
      </div>
    </>
  );
}

function TraceBlock({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-1 break-words text-sm leading-6 text-slate-800">
        {value || "-"}
      </p>
    </div>
  );
}
