<template>
	<dd class="log-event-timestamp">
		{{ log.timestamp | moment( "utc", "LT ll" ) }}
	</dd>
</template>

<script>
export default {
	name: 'EventTimestamp',
	props: {
		/**
		 * Log event to render.
		 */
		log: {
			type: Object,
			required: true
		}
	}
};
</script>
