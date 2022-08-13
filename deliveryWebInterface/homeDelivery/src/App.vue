<script setup>

import DeliverItem from "./components/DeliveryItem.vue";
import SearchPostcode from "./components/SearchPostcode.vue";

</script>

<template>
    <SearchPostcode />
    <DeliverItem deliveryItem="pizzahut" imageURI="PizzaHut.png" />
    <DeliverItem deliveryItem="dominos" imageURI="Dominos.png" />
    <DeliverItem deliveryItem="mcdonalds" imageURI="McDonalds.png" />
    <DeliverItem deliveryItem="kfc" imageURI="KFC.png" />
    <DeliverItem deliveryItem="burgerking" imageURI="BurgerKing.png" />
</template>

<style scoped>
</style>
