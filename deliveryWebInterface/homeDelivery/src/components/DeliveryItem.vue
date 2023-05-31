<script>

export default {
    
    data: () => ({
        postcode: null,
        requestURL: "http://localhost:8000",
        requestEndpoint: "/delivery/food/",
        canDeliver: null,
        status: "",
    }),

    props: {
        deliveryItem: String,
        imageURI: String
    },

    methods: {

        async getResponse () {
            this.status = "waiting";
            let self = this;
            await fetch(
                self.requestURL + self.requestEndpoint + self.deliveryItem + "?postcode=" + this.postcode,
                {
                    headers: {
                        "Content-Type": "application/json",
                    }
                }
            ).then(function(response) {
                return response.json();
            }).then(function(result) {
                self.status = result[self.deliveryItem]["can_deliver"];
            }).catch(function(error) {
                console.log("Something went wrong: " + error);
            });
        }

    }, 

    watch: {

        $route (newRoute, oldRoute) {
            this.postcode = newRoute.query.postcode;
            this.getResponse();
        }

    }

}

</script>

<template>
  <div id="delivery-item-container">
    <img :src="`/src/assets/DeliveryLogo/${this.imageURI}`" id="delivery-item-img" v-on:click="getResponse"/>
    <p id="status">{{ status }}</p>
  </div>
</template>

<style scoped>

#delivery-item-container {
    position: relative;
}

#delivery-item-img {
    height: 100px;
    margin: 1em;
}

#status {
    position: absolute;
    display: inline-block;

}

</style>
