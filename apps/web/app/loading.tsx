export default function Loading() {
  return (
    <div className="route-loading" role="status" aria-live="polite" aria-label="Loading page">
      <div className="route-loading-card">
        <div className="route-loading-mark" aria-hidden="true">
          <span className="route-loading-dot" />
          <span>Loading Percorium</span>
        </div>
        <div className="route-loading-track" aria-hidden="true">
          <span className="route-loading-bar" />
        </div>
      </div>
    </div>
  );
}
