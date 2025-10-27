import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

type Props = {
  title: string;
  data: any[];
  xKey: string;
  yKey: string;
  height?: number;
};

export default function LineChartCard({ title, data, xKey, yKey, height = 260 }: Props) {
  return (
    <div style={{ background:"#fff", border:"1px solid #eee", borderRadius:12, padding:16, marginTop:16 }}>
      <h3 style={{ margin:0, marginBottom:12 }}>{title}</h3>
      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey={yKey} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
