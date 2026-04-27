import { useMatch } from "react-router-dom";
import { useCompany } from "./api";

export function useCompanyContext() {
  const match = useMatch("/companies/:id");
  const idStr = match?.params.id;
  const id = idStr ? Number(idStr) : undefined;
  const { data } = useCompany(id);
  return { companyId: Number.isFinite(id) ? id : undefined, company: data };
}
