import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

type Row = { metric: string; value: number };

export function RadarScore({ data }: { data: Row[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data} outerRadius={90}>
        <PolarGrid stroke="#e5e8ef" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fill: "#5a6473", fontSize: 10, fontFamily: "JetBrains Mono" }}
        />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fill: "#8892a3", fontSize: 10 }}
          stroke="#e5e8ef"
        />
        <Radar
          dataKey="value"
          stroke="#06b6d4"
          fill="#06b6d4"
          fillOpacity={0.18}
          strokeWidth={1.75}
          isAnimationActive={false}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
