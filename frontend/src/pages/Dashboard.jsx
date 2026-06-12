import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowUpRight,
  Mail,
  ShieldAlert,
  Target,
} from "lucide-react";
import {
  fetchCategoryBreakdown,
  fetchDashboardStats,
  fetchSentimentTrend,
} from "../api/api";
import CategoryChart from "../components/CategoryChart";
import SentimentChart from "../components/SentimentChart";
import StatCard from "../components/StatCard";
import TopNavbar from "../components/TopNavbar";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [categories, setCategories] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsData, categoryData, sentimentData] = await Promise.all([
          fetchDashboardStats(),
          fetchCategoryBreakdown(),
          fetchSentimentTrend(),
        ]);
        if (!cancelled) {
          setStats(statsData);
          setCategories(categoryData);
          setSentiment(sentimentData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail?.message ||
              err?.message ||
              "Failed to load dashboard data"
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const avgConfidence =
    stats?.avg_confidence != null
      ? `${(stats.avg_confidence * 100).toFixed(1)}%`
      : "—";

  return (
    <>
      <TopNavbar
        title="Mission Control"
        subtitle="Real-time overview of email operations and AI triage performance"
      />

      <div className="flex-1 px-8 py-8">
        {error && (
          <div className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            title="Total Emails"
            value={loading ? "…" : (stats?.total_emails ?? 0).toLocaleString()}
            subtitle="All ingested messages"
            icon={Mail}
            accent="indigo"
          />
          <StatCard
            title="Escalations"
            value={loading ? "…" : (stats?.escalations ?? 0).toLocaleString()}
            subtitle="Requires human review"
            icon={ArrowUpRight}
            accent="rose"
          />
          <StatCard
            title="Critical Cases"
            value={loading ? "…" : (stats?.critical_cases ?? 0).toLocaleString()}
            subtitle="Critical urgency flagged"
            icon={ShieldAlert}
            accent="amber"
          />
          <StatCard
            title="Avg Confidence"
            value={loading ? "…" : avgConfidence}
            subtitle="Classifier certainty"
            icon={Target}
            accent="emerald"
          />
        </div>

        {!loading && stats?.spam_detected > 0 && (
          <div className="mt-5 flex items-center gap-2 rounded-xl border border-amber-200/80 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {stats.spam_detected} spam messages detected and filtered
          </div>
        )}

        <div className="mt-8 grid gap-6 xl:grid-cols-2">
          <CategoryChart data={categories} loading={loading} />
          <SentimentChart data={sentiment} loading={loading} />
        </div>
      </div>
    </>
  );
}
