import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Landing from "@/pages/landing";
import Dashboard from "@/pages/dashboard";
import LeadsDashboard from "@/pages/reddit-leads";
import Login from "@/pages/login";
import Businesses from "@/pages/businesses";
import BusinessEdit from "@/pages/business-edit";
import Platforms from "@/pages/platforms";
import Accounts from "@/pages/accounts";
import Notifications from "@/pages/notifications";
import Replies from "@/pages/replies";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <Route path="/login" component={Login} />
      <Route path="/dashboard">
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </Route>
      <Route path="/businesses">
        <ProtectedRoute>
          <Businesses />
        </ProtectedRoute>
      </Route>
      <Route path="/businesses/:id/edit">
        <ProtectedRoute>
          <BusinessEdit />
        </ProtectedRoute>
      </Route>
      <Route path="/leads">
        <ProtectedRoute>
          <LeadsDashboard />
        </ProtectedRoute>
      </Route>
      <Route path="/replies">
        <ProtectedRoute>
          <Replies />
        </ProtectedRoute>
      </Route>
      <Route path="/notifications">
        <ProtectedRoute>
          <Notifications />
        </ProtectedRoute>
      </Route>
      <Route path="/platforms">
        <ProtectedRoute>
          <Platforms />
        </ProtectedRoute>
      </Route>
      <Route path="/accounts">
        <ProtectedRoute>
          <Accounts />
        </ProtectedRoute>
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
