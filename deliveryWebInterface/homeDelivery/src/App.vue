<script setup>

import DeliverItem from "./components/DeliveryItem.vue";
import SearchPostcode from "./components/SearchPostcode.vue";

</script>

<template>
    <div id="main-container">
        <div class="full">
            <SearchPostcode />
        </div>
        <DeliverItem deliveryItem="pizzahut" imageURI="PizzaHut.png" />
        <DeliverItem deliveryItem="dominos" imageURI="Dominos.png" />
        <DeliverItem deliveryItem="mcdonalds" imageURI="McDonalds.png" />
        <DeliverItem deliveryItem="kfc" imageURI="KFC.png" />
        <DeliverItem deliveryItem="burgerking" imageURI="BurgerKing.png" />
    </div>
</template>

<style scoped>

#main-container {
    max-width: 500px;
    margin: auto;
}

.full {
    display: inline-block;
    width: 100%;
    margin-bottom: 5vw;
}

</style>
