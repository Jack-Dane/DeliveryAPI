import { createApp } from "vue/dist/vue.esm-bundler";
import { createRouter, createWebHistory } from "vue-router";
import Home from "./App.vue"

import './assets/main.css';

const routes = [
    { path: '/', name: "home", component: Home },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

const app = createApp({});

app.use(router);

app.mount('#app');
