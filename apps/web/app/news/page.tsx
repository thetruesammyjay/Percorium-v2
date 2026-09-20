import { TopStoriesFeed } from "@/components/news/TopStoriesFeed";

export default function NewsPage() {
  return (
    <section className="band band-gray news-page">
      <div className="page-shell">
        <div className="page-hero">
          <div>
            <p className="eyebrow">New · Tech and markets</p>
            <h1>Stay<br />ahead.</h1>
          </div>
          <div>
            <p>One feed for the events around the assets you trade. Stories stay informational and never change the approved mint list.</p>
          </div>
        </div>
        <TopStoriesFeed />
      </div>
    </section>
  );
}
