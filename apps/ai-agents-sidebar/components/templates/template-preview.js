"use client";
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplatePreview = TemplatePreview;
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
function TemplatePreview(_a) {
    var template = _a.template, onUse = _a.onUse;
    return (<div className="mt-3 sm:mt-4 border-t pt-3 sm:pt-4">
      <div className="flex justify-between items-center mb-1.5 sm:mb-2">
        <h4 className="font-medium text-xs sm:text-sm">Prévia do Template</h4>
        <button_1.Button variant="default" size="sm" className="h-7 sm:h-8 text-xs bg-purple-600 hover:bg-purple-700" onClick={function () { return onUse(template); }} aria-label={"Usar template ".concat(template.name)}>
          <lucide_react_1.Check className="mr-1 h-3 w-3 sm:h-3.5 sm:w-3.5" aria-hidden="true"/>
          Usar Este Template
        </button_1.Button>
      </div>
      <div className="bg-gray-50 p-2 sm:p-3 rounded-md border text-[10px] sm:text-xs font-mono h-[120px] sm:h-[150px] overflow-auto" aria-label="Prévia do conteúdo do template">
        {template.content.split("\n").map(function (line, i) { return (<div key={i} className="whitespace-pre-wrap">
            {line || "\u00A0"}
          </div>); })}
      </div>
    </div>);
}
