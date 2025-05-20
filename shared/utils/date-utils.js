"use strict";
// Funções utilitárias compartilhadas
// Implemente aqui utils reutilizáveis e use nos apps
Object.defineProperty(exports, "__esModule", { value: true });
exports.formatDate = void 0;
// Exemplo de função utilitária para manipulação de datas
var formatDate = function (date) {
    return date.toISOString().split('T')[0];
};
exports.formatDate = formatDate;
