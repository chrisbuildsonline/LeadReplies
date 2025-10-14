import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
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
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/businesses" component={Businesses} />
      <Route path="/businesses/:id/edit" component={BusinessEdit} />
      <Route path="/leads" component={LeadsDashboard} />
      <Route path="/replies" component={Replies} />
      <Route path="/notifications" component={Notifications} />
      <Route path="/platforms" component={Platforms} />
      <Route path="/accounts" component={Accounts} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
