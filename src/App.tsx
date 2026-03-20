import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import AllDecisions from "./pages/AllDecisions";
import Properties from "./pages/Properties";
import BusinessIdeas from "./pages/BusinessIdeas";
import Investments from "./pages/Investments";
import ContentIdeas from "./pages/ContentIdeas";
import DecisionDetail from "./pages/DecisionDetail";
import Compare from "./pages/Compare";
import ReviewQueue from "./pages/ReviewQueue";
import Rubrics from "./pages/Rubrics";
import Journal from "./pages/Journal";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="decisions" element={<AllDecisions />} />
          <Route path="decisions/:id" element={<DecisionDetail />} />
          <Route path="properties" element={<Properties />} />
          <Route path="business" element={<BusinessIdeas />} />
          <Route path="investments" element={<Investments />} />
          <Route path="content" element={<ContentIdeas />} />
          <Route path="compare" element={<Compare />} />
          <Route path="review" element={<ReviewQueue />} />
          <Route path="rubrics" element={<Rubrics />} />
          <Route path="journal" element={<Journal />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
