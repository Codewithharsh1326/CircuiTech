import { CircuitBoard, Network, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useDesignStore } from "@/stores/designStore";

export default function DashboardPanel() {
  const activeTab = useDesignStore((s) => s.activeTab);
  const setActiveTab = useDesignStore((s) => s.setActiveTab);
  const currentBom = useDesignStore((s) => s.currentBom);
  const pinConnections = useDesignStore((s) => s.pinConnections);
  const generatePinMap = useDesignStore((s) => s.generatePinMap);
  const isLoading = useDesignStore((s) => s.isLoading);

  const totalCost = currentBom.reduce(
    (sum, item) => sum + item.quantity * item.estimatedCost,
    0
  );

  return (
    <div className="flex h-full w-full flex-col bg-slate-950">
      {/* ── Main Header ──────────────────────────────────────── */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex size-8 items-center justify-center rounded-md bg-emerald-500/10">
            <CircuitBoard className="size-4 text-emerald-400" />
          </div>
          <h1 className="text-base font-semibold tracking-tight text-slate-100">
            CircuiTech <span className="text-slate-500 font-normal">Workspace</span>
          </h1>
        </div>
        <Badge
          variant="secondary"
          className="bg-slate-900 text-slate-400 border-slate-800"
        >
          {currentBom.length} parts · ${totalCost.toFixed(2)}
        </Badge>
      </header>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex min-h-0 flex-1 flex-col"
      >
        {/* ── Tab bar ───────────────────────────────────────── */}
        <div className="flex items-center border-b border-slate-800/60 px-6 py-2">
          <TabsList className="bg-slate-900/50">
            <TabsTrigger
              value="bom"
              className="gap-2 px-4 py-1.5 data-[state=active]:bg-slate-800 data-[state=active]:text-emerald-400"
            >
              <CircuitBoard className="size-4" />
              BOM
            </TabsTrigger>
            <TabsTrigger
              value="pinmap"
              className="gap-2 px-4 py-1.5 data-[state=active]:bg-slate-800 data-[state=active]:text-emerald-400"
            >
              <Network className="size-4" />
              Pin Map
            </TabsTrigger>
          </TabsList>
        </div>

        {/* ── BOM Tab ───────────────────────────────────────── */}
        <TabsContent value="bom" className="mt-0 flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-4">
              <Table>
                <TableHeader>
                  <TableRow className="border-slate-800 hover:bg-transparent">
                    <TableHead className="text-slate-400">#</TableHead>
                    <TableHead className="text-slate-400">
                      Part Number
                    </TableHead>
                    <TableHead className="text-slate-400">
                      Manufacturer
                    </TableHead>
                    <TableHead className="text-slate-400">
                      Description
                    </TableHead>
                    <TableHead className="text-right text-slate-400">
                      Qty
                    </TableHead>
                    <TableHead className="text-right text-slate-400">
                      Unit Cost
                    </TableHead>
                    <TableHead className="text-right text-slate-400">
                      Line Total
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentBom.length === 0 && (
                    <TableRow className="border-0 hover:bg-transparent">
                      <TableCell colSpan={7} className="h-48 text-center text-slate-500 font-medium">
                        Your generated components will appear here. Start a conversation with the Co-Pilot to build an embedded BOM.
                      </TableCell>
                    </TableRow>
                  )}
                  {currentBom.map((item, idx) => (
                    <TableRow
                      key={item.partNumber + idx.toString()}
                      className="border-slate-800/60 hover:bg-slate-900/60"
                    >
                      <TableCell className="font-mono text-xs text-slate-600">
                        {idx + 1}
                      </TableCell>
                      <TableCell className="font-mono text-sm text-emerald-400">
                        {item.partNumber}
                      </TableCell>
                      <TableCell className="text-sm text-slate-300">
                        {item.manufacturer || "Unknown"}
                      </TableCell>
                      <TableCell className="max-w-[280px] truncate text-sm text-slate-400">
                        {item.description}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-slate-300">
                        {item.quantity}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-slate-400">
                        ${item.estimatedCost.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-slate-200">
                        $
                        {(item.quantity * item.estimatedCost).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {currentBom.length > 0 && (
                <div className="mt-6 flex justify-end px-2">
                  <Button
                    className="gap-2 bg-emerald-600 hover:bg-emerald-500 text-white"
                    onClick={() => generatePinMap()}
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Network className="size-4" />
                    )}
                    Generate Pin Map
                  </Button>
                </div>
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        {/* ── Pin Map Tab ───────────────────────────────────── */}
        <TabsContent value="pinmap" className="mt-0 flex-1 p-4 overflow-hidden">
          <Card className="flex h-full flex-col border-slate-800 bg-slate-900/50">
            <CardHeader className="shrink-0">
              <CardTitle className="flex items-center gap-2 text-slate-200">
                <Network className="size-5 text-emerald-400" />
                Pin Map
              </CardTitle>
              <CardDescription className="text-slate-500">
                Hardware pin connections between components generated by the AI agent.
              </CardDescription>
            </CardHeader>
            <CardContent className="min-h-0 flex-1 p-0">
              <ScrollArea className="h-full px-6 pb-6">
                {isLoading && (
                  <div className="flex h-48 flex-col items-center justify-center gap-4 text-emerald-500">
                    <Loader2 className="size-8 animate-spin" />
                    <p className="text-sm">Synthesizing logical connections...</p>
                  </div>
                )}
                {!isLoading && pinConnections.length === 0 && (
                  <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-950/50">
                    <p className="text-sm text-slate-600">
                      No pin assignments yet.
                    </p>
                  </div>
                )}
                {!isLoading && pinConnections.length > 0 && (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-slate-800">
                        <TableHead className="text-slate-400">Source Component</TableHead>
                        <TableHead className="text-slate-400">Source Pin</TableHead>
                        <TableHead className="text-slate-400">Target Component</TableHead>
                        <TableHead className="text-slate-400">Target Pin</TableHead>
                        <TableHead className="text-slate-400">Signal Type</TableHead>
                        <TableHead className="text-slate-400">Notes</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pinConnections.map((conn, i) => (
                        <TableRow key={i} className="border-slate-800/60 hover:bg-slate-900/60">
                          <TableCell className="font-mono text-xs text-slate-300">{conn.source_part}</TableCell>
                          <TableCell className="font-mono text-sm text-emerald-400">{conn.source_pin}</TableCell>
                          <TableCell className="font-mono text-xs text-slate-300">{conn.target_part}</TableCell>
                          <TableCell className="font-mono text-sm text-emerald-400">{conn.target_pin}</TableCell>
                          <TableCell className="text-sm">
                            <Badge variant="outline" className="border-slate-700 bg-slate-900 text-slate-400">
                              {conn.signal_type}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-slate-500">{conn.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
