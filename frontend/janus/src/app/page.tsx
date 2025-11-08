import Canvas from "@/components/Canvas";
import CanvasWithPolling from "@/components/CanvasWithPolling";

export default function Home() {
  return (
    <div className="h-screen w-screen">
      <CanvasWithPolling />
    </div>
  );
}
