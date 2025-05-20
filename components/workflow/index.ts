import * as React from "react";

// Exportação dos componentes de workflow
export const NodeCategory = React.lazy(() => import("./node-category").then(module => ({ default: module.NodeCategory })));
export const NodeForm = React.lazy(() => import("./node-form").then(module => ({ default: module.NodeForm })));
export const NodeSidebar = React.lazy(() => import("./node-sidebar").then(module => ({ default: module.NodeSidebar })));
export const NodeTemplateCard = React.lazy(() => import("./node-template-card").then(module => ({ default: module.NodeTemplateCard })));

// Exportação padrão para facilitar importações
const WorkflowComponents = {
  NodeCategory,
  NodeForm,
  NodeSidebar,
  NodeTemplateCard
};

export default WorkflowComponents;
