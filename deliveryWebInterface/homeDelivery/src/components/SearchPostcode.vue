
<script>

export default {

    data: () => ({
        postcode: null,
    }),

    methods: {
        changePostcode () {
            this.$router.push({name: "home", query: {"postcode": this.postcode}});
        }
    }

}

</script>

<template>
    <div id="postcode-search-container">
        <input type="text" placeholder="Postcode" v-model="postcode" id="postcode-search"/>
        <button v-on:click="changePostcode" id="postcode-submit">
            <img :src="`/src/assets/DeliveryLogo/search-icon.png`" alt="search">
        </button>
    </div>
</template>

<style scoped>

#postcode-search-container {
    background-color: white;
    border-radius: 30px;
    display: inline-block;
}

input, button {
    all: unset;
    padding: 10px;
    font-size: x-large;
}

button {
    background-color: #c5bd3a;
    width: 40px;
    height: 40px;
    border-radius: 30px;
}

img {
    position: relative;
    left: 5px;
    top: 5px;
    max-width: 30px;
}

</style>
