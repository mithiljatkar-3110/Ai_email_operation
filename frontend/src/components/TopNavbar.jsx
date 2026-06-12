export default function TopNavbar({ title, subtitle }) {
  return (
    <header className="border-b border-slate-200/80 bg-white/80 px-8 py-5 backdrop-blur">
      <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
    </header>
  );
}
