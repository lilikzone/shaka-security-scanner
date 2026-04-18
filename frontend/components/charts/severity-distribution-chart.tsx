"use client";

import { severityDistribution } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

export function SeverityDistributionChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Severity Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-72 w-full">
          <ResponsiveContainer>
            <PieChart>
              <Pie data={severityDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={65} outerRadius={95}>
                {severityDistribution.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "10px"
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
