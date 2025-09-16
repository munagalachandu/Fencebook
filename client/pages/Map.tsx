import { useState } from "react";
import MapLegend from "@/components/MapLegend";
import MapView from "@/components/MapView";
import MapSidebar from "@/components/Mapsidebar";

interface Filters {
  safe: boolean;
  warning: boolean;
  alert: boolean;
  sensorNode: boolean;
  camera: boolean;
  gateway: boolean;
}

export default function Map() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    safe: true,
    warning: true,
    alert: true,
    sensorNode: true,
    camera: true,
    gateway: true,
  });

  return (
    <div className="w-full h-screen sentinel-bg">
      <div className="flex h-full gap-4 p-4">
        <div className="shrink-0">
          <MapSidebar
            isCollapsed={isCollapsed}
            onToggleCollapse={() => setIsCollapsed((v) => !v)}
            filters={filters}
            onFilterChange={setFilters}
          />
        </div>

        <div className="flex-1 flex flex-col gap-4 min-w-0">
          <div className="flex-1 min-h-0">
            <MapView />
          </div>

          <div className="w-full md:w-auto md:self-end">
            <MapLegend />
          </div>
        </div>
      </div>
    </div>
  );
}