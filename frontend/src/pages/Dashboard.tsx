import { useEffect, useMemo, useState } from "react";
import { listPatients, getReadings24h, listTelemetry } from "../api/endpoints";
import AppLayout from "../components/layout/AppLayout";
import StatCard from "../components/ui/StatCard";
import LineChartCard from "../components/LineChartCard";

type Patient = { id: number; full_name: string; email?: string|null };

export default function Dashboard() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [deviceId, setDeviceId] = useState<number>(1);
  const [readings, setReadings] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<any[]>([]);

  useEffect(() => { listPatients().then(setPatients).catch(()=>setPatients([])); }, []);
  useEffect(() => {
    getReadings24h(deviceId).then(setReadings);
    const from = new Date(Date.now() - 24*3600*1000).toISOString();
    listTelemetry(deviceId, from).then(setTelemetry);
  }, [deviceId]);

  const last = readings?.[0];
  const hr   = last?.heart_rate_bpm ?? last?.heart_rate ?? "-";
  const spo2 = last?.spo2_pct ?? last?.spo2 ?? "-";
  const temp = last?.temp_c ?? "-";
  const batt = telemetry?.[0]?.battery_pct ?? "-";

  const readingsData = useMemo(() => (readings || []).map((r: any) => ({
    time: new Date(r.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    hr: r.heart_rate_bpm ?? r.heart_rate ?? null,
  })), [readings]);

  const batteryData = useMemo(() => (telemetry || []).map((t: any) => ({
    time: new Date(t.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    batt: t.battery_pct,
  })), [telemetry]);

  return (
    <AppLayout>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <div className="text-sm">
          Device ID:&nbsp;
          <input
            className="border rounded px-2 py-1 w-24"
            value={deviceId}
            onChange={e=>setDeviceId(Number(e.target.value||1))}
          />
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="FC actual" value={hr} unit="bpm" />
        <StatCard label="SpO₂" value={spo2} unit="%" />
        <StatCard label="Temperatura" value={temp} unit="°C" />
        <StatCard label="Batería" value={batt} unit="%" />
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChartCard title="Frecuencia cardíaca (24h)" data={readingsData} xKey="time" yKey="hr" />
        <LineChartCard title="Batería (24h)" data={batteryData} xKey="time" yKey="batt" />
      </div>

      <div className="mt-8">
        <h3 className="text-lg font-medium mb-2">Pacientes</h3>
        <ul className="list-disc pl-6 text-sm">
          {patients.map(p => <li key={p.id}>{p.full_name}{p.email ? ` (${p.email})` : ""}</li>)}
        </ul>
      </div>
    </AppLayout>
  );
}
