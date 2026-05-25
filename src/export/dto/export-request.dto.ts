import { IsEnum, IsString, IsNotEmpty, IsArray, IsOptional } from "class-validator";
import { ExportFields } from "./export-fields.enum";
import { ExportRecords } from "./export-records.enum";
import { ExportFormat } from "./export-format.enum";

export class ExportRequestDto {
    @IsString()
    @IsNotEmpty()
    resource!: string;

    @IsEnum(ExportFields)
    exportFields!: ExportFields;

    @IsEnum(ExportRecords)
    exportRecords!: ExportRecords;

    @IsEnum(ExportFormat)
    format!: ExportFormat;

    @IsString()
    @IsNotEmpty()
    filename!: string;

    @IsArray()
    @IsString({ each: true })
    @IsOptional()
    fields?: string[];

    @IsOptional()
    records?: number[];
}