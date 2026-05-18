import  { Body, Controller, Get } from "@nestjs/common";
import  { FileService } from "./file.service";
import type { SignedUploadLinkRequest } from "./dto/signed-upload-link-request.dto";
import type { SignedUploadLinkResponse } from "./dto/signed-upload-link-response.dto";

@Controller("file")
export class FileController {
    constructor(private readonly fileService: FileService) { }

    @Get("upload")
    public async getSignedUploadLink(@Body() body: SignedUploadLinkRequest): Promise<SignedUploadLinkResponse> {
        return this.fileService.getSignedUploadUrl(body);
    }
}