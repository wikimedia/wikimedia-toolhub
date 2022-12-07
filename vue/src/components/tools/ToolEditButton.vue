<template>
	<v-menu
		v-if="$can( 'change', tool )"
		offset-y
	>
		<template #activator="{ on, attrs }">
			<v-btn
				color="primary base100--text my-1 mx-2"
				:small="$vuetify.breakpoint.smAndDown"
				v-bind="attrs"
				v-on="on"
			>
				<v-icon class="me-2">
					mdi-pencil
				</v-icon>
				{{ $t( 'tools-edit-button' ) }}
			</v-btn>
		</template>
		<v-list nav>
			<v-list-item
				:to="{
					name: 'tools-edit',
					params: { name: tool.name }
				}"
				link
			>
				<v-list-item-icon>
					<v-icon>
						mdi-file-document-edit-outline
					</v-icon>
				</v-list-item-icon>
				<v-list-item-title>
					{{ $t( 'tools-edit-core' ) }}
				</v-list-item-title>
			</v-list-item>
			<v-list-item
				:to="{
					name: 'tools-edit-annotations',
					params: { name: tool.name }
				}"
				link
			>
				<v-list-item-icon>
					<v-icon>
						mdi-pencil-box-multiple-outline
					</v-icon>
				</v-list-item-icon>
				<v-list-item-title>
					{{ $t( 'tools-edit-annotations' ) }}
				</v-list-item-title>
			</v-list-item>
		</v-list>
	</v-menu>
	<v-btn
		v-else-if="$can( 'change', 'toolinfo/annotations' )"
		:to="{
			name: 'tools-edit-annotations',
			params: { name: tool.name }
		}"
		color="primary base100--text my-1 mx-2"
		:small="$vuetify.breakpoint.smAndDown"
	>
		<v-icon class="me-2">
			mdi-pencil
		</v-icon>
		{{ $t( 'tools-edit-button' ) }}
	</v-btn>
</template>

<script>
export default {
	name: 'ToolEditButton',
	props: {
		tool: {
			type: Object,
			default: null
		}
	}
};
</script>
