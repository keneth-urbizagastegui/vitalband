export default function StatCard({
  label, value, unit
}: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="bg-white rounded-xl border p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">
        {value}{unit ? <span className="text-slate-400 text-base ml-1">{unit}</span> : null}
      </div>
    </div>
  );
}
