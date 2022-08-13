import { createApp } from "vue/dist/vue.esm-bundler";
import { createRouter, createWebHistory } from "vue-router";
import Home from "./App.vue"

import './assets/main.css';

const About = { template: '<div>About</div>' };

const routes = [
    { path: '/', name: "home", component: Home },
    { path: '/about', component: About },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

const app = createApp({});

app.use(router);

app.mount('#app');
