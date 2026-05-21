export class AppResponse {
    public status!: number;
    public message!: string;

    constructor(status?: number) {
        if (status) this.status = status;
    }
}