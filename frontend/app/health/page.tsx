export default function HealthPage() {
  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-semibold tracking-tight">Health</h1>
      <p className="text-muted-foreground text-sm">
        Frontend shell is up. Wire this to{' '}
        <code className="font-mono text-xs">GET /api/v1/health/</code> when the
        API is running.
      </p>
    </div>
  );
}
