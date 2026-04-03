import Link from 'next/link';

export default function ForbiddenPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-5xl font-bold tracking-tight">403</h1>
      <p className="text-muted-foreground max-w-md text-lg">
        You do not have permission to view this page. If you believe this is an
        error, contact your administrator.
      </p>
      <Link
        href="/"
        className="bg-primary text-primary-foreground hover:bg-primary/90 mt-2 inline-flex h-9 items-center rounded-lg px-4 text-sm font-medium"
      >
        Back to Home
      </Link>
    </div>
  );
}
